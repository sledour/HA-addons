# 0.2.0 - Stable with DB
import requests
import logging

logger = logging.getLogger(__name__)

class TMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def search_multi(self, title, year=None):
        """
        Cherche sur TMDB sans distinction de type (Movie/TV) 
        pour corriger les erreurs de type de Plex.
        """
        url = f"{self.base_url}/search/multi"
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "fr-FR",
            "include_adult": "false"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            results = response.json().get('results', [])
            
            for res in results:
                res_type = res.get('media_type') # 'movie' ou 'tv'
                if res_type not in ['movie', 'tv']: continue
                
                res_date = res.get('release_date') or res.get('first_air_date') or ""
                res_year = res_date[:4]
                
                # Si l'année correspond (ou si on n'a pas d'année de comparaison)
                if not year or res_year == str(year):
                    return {
                        "tmdb_id": res.get('id'),
                        "type": res_type, # On récupère le VRAI type TMDB
                        "title": res.get('title') or res.get('name')
                    }
            return None
        except Exception as e:
            logger.error(f"Erreur recherche TMDB pour {title}: {e}")
            return None
        
    def get_media_details(self, title, media_type):
        search_type = "movie" if media_type == "movie" else "tv"
        url = f"{self.base_url}/search/{search_type}"
        params = {"api_key": self.api_key, "query": title, "language": "fr-FR"}
        
        try:
            r = requests.get(url, params=params)
            results = r.json().get('results', [])
            if results:
                first = results[0]
                return {
                    "tmdb_id": first['id'],
                    "title": first.get('title') or first.get('name'),
                    "poster_path": first.get('poster_path') # On récupère le /xxxxx.jpg
                }
        except Exception as e:
            logger.error(f"Erreur TMDB pour {title}: {e}")
        return None