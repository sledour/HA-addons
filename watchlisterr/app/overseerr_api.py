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

    def get_users(self):
        try:
            response = requests.get(f"{self.url}/api/v1/user", headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erreur Overseerr get_users: {e}")
            return []

    def search_content(self, title, year, media_type):
        """Recherche un contenu et retourne son statut Overseerr."""
        try:
            # Encodage du titre pour l'URL
            query = requests.utils.quote(title)
            url = f"{self.url}/api/v1/search?query={query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            results = response.json().get('results', [])
            
            for res in results:
                # Filtrage par type (movie vs tv)
                if res.get('mediaType') != media_type:
                    continue
                
                # Vérification de l'année
                res_date = res.get('releaseDate') if media_type == 'movie' else res.get('firstAirDate')
                res_year = res_date[:4] if res_date else None
                
                # On accepte si l'année correspond ou si elle est absente (cas fréquent sur les nouveautés)
                if not year or not res_year or str(year) == res_year:
                    media_info = res.get('mediaInfo', {})
                    # mediaInfo status : 1 = UNKNOWN, 2 = PENDING, 3 = PROCESSING, 4 = PARTIALLY_AVAILABLE, 5 = AVAILABLE
                    status_code = media_info.get('status', 1)
                    
                    status_map = {
                        1: "Manquant (Disponible au téléchargement)",
                        2: "En attente d'approbation",
                        3: "En cours de téléchargement",
                        4: "Partiellement disponible",
                        5: "Déjà présent sur Plex"
                    }
                    
                    return {
                        "tmdb_id": res.get('id'),
                        "status": status_map.get(status_code, "Inconnu"),
                        "can_request": status_code == 1 
                    }
            return {"tmdb_id": None, "status": "Non trouvé sur Overseerr", "can_request": False}
        except Exception as e:
            logger.error(f"Erreur recherche Overseerr ({title}): {e}")
            return {"tmdb_id": None, "status": "Erreur API", "can_request": False}