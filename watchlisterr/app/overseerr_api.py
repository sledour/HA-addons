# Stable version 0.1.0
import requests
import logging

logger = logging.getLogger(__name__)

class OverseerrClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.headers = {"X-Api-Key": api_key}

    def get_users(self):
        """Récupère la liste des utilisateurs Overseerr pour le mapping avec Plex"""
        url = f"{self.base_url}/api/v1/user"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Erreur lors de la récupération des utilisateurs Overseerr : {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Erreur connexion Overseerr (get_users) : {e}")
            return []

    def get_media_status(self, tmdb_id, media_type):
        """Vérifie le statut par ID TMDB (recommandé)"""
        # Overseerr attend 'tv' et non 'show'
        m_type = "tv" if media_type in ["show", "tv"] else "movie"
        
        url = f"{self.base_url}/api/v1/{m_type}/{tmdb_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                media = data.get('mediaInfo', {})
                status = media.get('status', 1)
                
                # Mappage officiel Overseerr
                # 1: Unknown, 2: Pending, 3: Processing, 4: Partially Available, 5: Available
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
        """Fallback recherche textuelle si le TMDB ID est absent"""
        url = f"{self.base_url}/api/v1/search"
        params = {"query": title}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                for res in results:
                    # On compare le type (converti en 'movie' ou 'tv')
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