# 0.3.0 - Reactive Loop + Submit Request
import requests
import logging

logger = logging.getLogger(__name__)

class OverseerrClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.headers = {"X-Api-Key": api_key}

    def submit_request(self, tmdb_id, media_type, user_id, title, is_simulation=True):
        """Soumet une requête à Overseerr"""
        
        if is_simulation:
            logger.info(f"🧪 [SIMULATION] Requête pour '{title}' (ID:{tmdb_id}) | User ID:{user_id}")
            return True

        # --- MODE PRODUCTION ---
        url = f"{self.base_url}/api/v1/request"
        
        # Déterminer le type correct
        is_tv = media_type in ["show", "tv"]
        
        payload = {
            "mediaType": "tv" if is_tv else "movie",
            "mediaId": int(tmdb_id),
            "userId": int(user_id) if user_id else None
        }

        # AJOUT CRUCIAL : Overseerr a besoin de savoir quelles saisons demander
        if is_tv:
            payload["seasons"] = "all" 

        try:
            r = requests.post(url, json=payload, headers=self.headers, timeout=15)
            if r.status_code == 201:
                logger.info(f"🚀 [LIVE] Succès ! '{title}' est maintenant en cours de traitement sur UltraCC.")
                return True
            elif r.status_code == 409:
                logger.warning(f"⚠️ [LIVE] '{title}' est déjà demandé dans Overseerr.")
                return True
            else:
                logger.error(f"❌ [LIVE] Erreur Overseerr ({r.status_code}): {r.text}")
                return False
        except Exception as e:
            logger.error(f"❌ [LIVE] Erreur critique lors de l'envoi : {e}")
            return False
        
    def get_users(self):
        url = f"{self.base_url}/api/v1/user"
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                return data.get('results', []) 
            else:
                logger.error(f"Erreur Overseerr get_users: {r.status_code}")
                return []
        except Exception as e:
            logger.error(f"Erreur connexion Overseerr: {e}")
            return []
    
    def get_media_status(self, tmdb_id, media_type):
        m_type = "tv" if media_type in ["show", "tv"] else "movie"
        url = f"{self.base_url}/api/v1/{m_type}/{tmdb_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                media = data.get('mediaInfo', {})
                status = media.get('status', 1)
                status_map = {
                    1: "Non demandé", 
                    2: "En attente", 
                    3: "Approuvé (En cours)", 
                    4: "Partiellement disponible", 
                    5: "Déjà présent sur Plex"
                }
                return {
                    "status": status_map.get(status, "Inconnu"),
                    "can_request": status == 1,
                    "tmdb_id": tmdb_id
                }
            return {"status": "Non trouvé sur Overseerr", "can_request": True, "tmdb_id": tmdb_id}
        except Exception as e:
            logger.error(f"Erreur statut Overseerr pour ID {tmdb_id}: {e}")
            return {"status": "Erreur API", "can_request": False, "tmdb_id": tmdb_id}

    def search_content(self, title, year, media_type):
        url = f"{self.base_url}/api/v1/search"
        params = {"query": title}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                for res in results:
                    target_type = "tv" if media_type in ["show", "tv"] else "movie"
                    if res.get('mediaType') == target_type:
                        res_date = res.get('releaseDate', res.get('firstAirDate', ''))
                        res_year = res_date[:4] if res_date else ""
                        if not year or res_year == str(year):
                            return self.get_media_status(res.get('id'), target_type)
            return {"status": "Introuvable", "can_request": True, "tmdb_id": None}
        except Exception as e:
            logger.error(f"Erreur recherche Overseerr pour {title}: {e}")
            return {"status": "Erreur Recherche", "can_request": False, "tmdb_id": None}