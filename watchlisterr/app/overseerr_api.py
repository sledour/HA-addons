import requests
import logging

logger = logging.getLogger(__name__)

class OverseerrClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.headers = {"X-Api-Key": api_key}

    def get_media_status(self, tmdb_id, media_type):
        """Vérifie le statut par ID TMDB (recommandé)"""
        url = f"{self.base_url}/api/v1/{media_type}/{tmdb_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                media = data.get('mediaInfo', {})
                status = media.get('status', 1)
                
                status_map = {1: "Inconnu", 2: "En attente", 3: "Approuvé", 4: "Disponible", 5: "Déjà présent sur Plex"}
                return {
                    "status": status_map.get(status, "Inconnu"),
                    "can_request": status == 1,
                    "tmdb_id": tmdb_id
                }
            return {"status": "Non trouvé", "can_request": True}
        except Exception:
            return {"status": "Erreur API", "can_request": False}

    def search_content(self, title, year, media_type):
        """Fallback recherche textuelle"""
        url = f"{self.base_url}/api/v1/search"
        params = {"query": title}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            results = response.json().get('results', [])
            for res in results:
                if res.get('mediaType') == media_type:
                    res_year = res.get('releaseDate', res.get('firstAirDate', ''))[:4]
                    if not year or res_year == str(year):
                        return self.get_media_status(res.get('id'), media_type)
            return {"status": "Manquant", "can_request": True}
        except Exception:
            return {"status": "Erreur Recherche", "can_request": False}