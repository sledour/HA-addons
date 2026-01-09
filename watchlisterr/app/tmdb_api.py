# 0.2.0 - Stable with DB
import requests
import logging

logger = logging.getLogger(__name__)

class TMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def search_multi(self, title, year=None, target_id=None):
        url = "https://api.themoviedb.org/3/search/multi"
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "fr-FR"
        }
        
        try:
            r = requests.get(url, params=params, timeout=5)
            results = r.json().get('results', [])
            
            if not results:
                return None

            # --- LOGIQUE DE SÉLECTION ---
            
            # Cas 1 : On a un ID cible (le plus précis)
            if target_id:
                for res in results:
                    if str(res.get("id")) == str(target_id):
                        return {
                            "tmdb_id": res.get("id"),
                            "type": res.get("media_type", "movie"),
                            "poster_path": res.get("poster_path")
                        }

            # Cas 2 : On n'a pas d'ID, mais on a une année (validation par date)
            if year:
                for res in results:
                    res_date = res.get("release_date") or res.get("first_air_date")
                    if res_date and str(year) in res_date:
                        return {
                            "tmdb_id": res.get("id"),
                            "type": res.get("media_type", "movie"),
                            "poster_path": res.get("poster_path")
                        }

            # Cas 3 : Fallback (on prend le premier film/série, on évite les personnes)
            for res in results:
                if res.get("media_type") in ["movie", "tv"]:
                    return {
                        "tmdb_id": res.get("id"),
                        "type": res.get("media_type"),
                        "poster_path": res.get("poster_path")
                    }
                    
        except Exception as e:
            print(f"Erreur TMDB: {e}")
        return None