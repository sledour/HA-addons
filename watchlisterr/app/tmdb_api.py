# 0.2.0 - Stable with DB
import requests
import logging

logger = logging.getLogger(__name__)

class TMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def search_multi(self, title, year=None):
        url = f"https://api.themoviedb.org/3/search/multi"
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "fr-FR"
        }
        try:
            r = requests.get(url, params=params, timeout=5)
            data = r.json()
            results = data.get('results', [])
            
            if results:
                # On prend le premier résultat
                res = results[0]
                
                # On extrait DIRECTEMENT les infos sans refaire d'appel
                return {
                    "tmdb_id": res.get("id"),
                    "type": res.get("media_type", "movie"),
                    "poster_path": res.get("poster_path") # C'est ici que se trouve /xUuH...jpg
                }
        except Exception as e:
            print(f"Erreur TMDB Search: {e}")
        return None