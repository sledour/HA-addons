# 0.2.0 - Stable with DB
import requests
import logging

logger = logging.getLogger(__name__)

class TMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def search_multi(self, title, year=None, target_id=None, media_type=None):
        # 1. Détermination de l'URL selon le type de média Plex
        # Plex utilise 'movie' ou 'show'/'tv'
        if media_type == 'movie':
            endpoint = "search/movie"
        elif media_type in ['tv', 'show']:
            endpoint = "search/tv"
        else:
            endpoint = "search/multi"

        url = f"https://api.themoviedb.org/3/{endpoint}"
        
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "fr-FR"
        }

        # 2. Ajout du filtre année directement dans la requête API pour plus de précision
        if year:
            if endpoint == "search/movie":
                params["primary_release_year"] = year
            elif endpoint == "search/tv":
                params["first_air_date_year"] = year

        try:
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            results = r.json().get('results', [])
            
            if not results:
                return None

            # --- LOGIQUE DE SÉLECTION ---
            
            # Cas 1 : On a un ID cible (priorité absolue)
            if target_id:
                for res in results:
                    if str(res.get("id")) == str(target_id):
                        return {
                            "tmdb_id": res.get("id"),
                            "type": res.get("media_type") or media_type.replace('show', 'tv'),
                            "poster_path": res.get("poster_path")
                        }

            # Cas 2 : Filtrage intelligent des résultats
            for res in results:
                # On ignore les résultats qui ne sont pas des films ou séries (ex: personnes)
                m_type = res.get("media_type") or endpoint.split('/')[-1]
                if m_type not in ["movie", "tv"]:
                    continue
                    
                # Si on a cherché un type spécifique, on s'assure que le résultat correspond
                # Note: TMDB renvoie 'tv' même si Plex dit 'show'
                mapped_type = "tv" if m_type == "show" else m_type
                
                # Si on a une année, on valide la correspondance
                if year:
                    res_date = res.get("release_date") or res.get("first_air_date")
                    if res_date and str(year) in res_date:
                        return {
                            "tmdb_id": res.get("id"),
                            "type": mapped_type,
                            "poster_path": res.get("poster_path")
                        }
                else:
                    # Si pas d'année, on prend le premier résultat valide
                    return {
                        "tmdb_id": res.get("id"),
                        "type": mapped_type,
                        "poster_path": res.get("poster_path")
                    }
                    
        except Exception as e:
            print(f"Erreur TMDB: {e}")
        return None