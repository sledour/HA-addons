import requests
import logging

logger = logging.getLogger(__name__)

class OverseerrClient:
    def __init__(self, url, api_key):
        self.url = url.rstrip('/')
        self.headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }
        self.status_map = {
            1: "Manquant",
            2: "En attente",
            3: "En cours",
            4: "Partiellement disponible",
            5: "Déjà présent sur Plex"
        }

    def get_status(self):
        """Vérifie la connexion et récupère la version d'Overseerr."""
        try:
            response = requests.get(f"{self.url}/api/v1/settings/about", headers=self.headers, timeout=5)
            if response.status_code == 200:
                return {"connected": True, "details": response.json()}
            return {"connected": False, "error": f"Code HTTP {response.status_code}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def get_users(self):
        """Récupère la liste des utilisateurs Overseerr."""
        try:
            response = requests.get(f"{self.url}/api/v1/user", headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erreur Overseerr get_users: {e}")
            return []

    def get_media_status(self, tmdb_id, media_type):
        """Récupère le statut directement via l'ID TMDB."""
        try:
            endpoint = f"movie/{tmdb_id}" if media_type == "movie" else f"tv/{tmdb_id}"
            url = f"{self.url}/api/v1/{endpoint}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                media_info = data.get('mediaInfo', {})
                status_code = media_info.get('status', 1)
                
                return {
                    "tmdb_id": tmdb_id,
                    "status": self.status_map.get(status_code, "Inconnu"),
                    "can_request": status_code == 1 
                }
            return {"tmdb_id": tmdb_id, "status": "Non trouvé", "can_request": False}
        except Exception as e:
            logger.error(f"Erreur status direct Overseerr ({tmdb_id}): {e}")
            return {"tmdb_id": tmdb_id, "status": "Erreur API", "can_request": False}

    def search_content(self, title, year, media_type):
        """Recherche agressive avec filtrage strict par année et type."""
        try:
            query = requests.utils.quote(title)
            url = f"{self.url}/api/v1/search?query={query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            results = response.json().get('results', [])
            
            for res in results:
                # 1. Filtre strict sur le type
                if res.get('mediaType') != media_type:
                    continue
                
                # 2. Extraction de l'année
                res_date = res.get('releaseDate') if media_type == 'movie' else res.get('firstAirDate')
                res_year = res_date[:4] if res_date else None
                
                # 3. FILTRAGE AGRESSIF : L'année DOIT correspondre si elle est connue
                # Cela évite de confondre le film de 2024 avec une version de 1998
                if year and res_year:
                    if str(year) != str(res_year):
                        continue # Année différente, on passe au résultat suivant

                # 4. Match trouvé !
                media_info = res.get('mediaInfo', {})
                status_code = media_info.get('status', 1)
                
                # Log pour le debug
                match_title = res.get('title') or res.get('name')
                logger.info(f"Match Overseerr : '{title}' ({year}) -> '{match_title}' ({res_year}) | ID: {res.get('id')}")

                return {
                    "tmdb_id": res.get('id'),
                    "status": self.status_map.get(status_code, "Inconnu"),
                    "can_request": status_code == 1 
                }
                
            return {"tmdb_id": None, "status": "Non trouvé", "can_request": False}
        except Exception as e:
            logger.error(f"Erreur recherche Overseerr ({title}): {e}")
            return {"tmdb_id": None, "status": "Erreur API", "can_request": False}