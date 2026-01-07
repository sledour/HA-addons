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

    def search_content(self, title, year, media_type):
        """Recherche un contenu et retourne son statut de disponibilité."""
        try:
            query = requests.utils.quote(title)
            url = f"{self.url}/api/v1/search?query={query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            results = response.json().get('results', [])
            
            for res in results:
                # Filtrage strict par type
                if res.get('mediaType') != media_type:
                    continue
                
                # Vérification de l'année
                res_date = res.get('releaseDate') if media_type == 'movie' else res.get('firstAirDate')
                res_year = res_date[:4] if res_date else None
                
                if not year or not res_year or str(year) == res_year:
                    media_info = res.get('mediaInfo', {})
                    status_code = media_info.get('status', 1)
                    
                    status_map = {
                        1: "Manquant",
                        2: "En attente",
                        3: "En cours",
                        4: "Partiellement disponible",
                        5: "Déjà présent sur Plex"
                    }
                    
                    return {
                        "tmdb_id": res.get('id'),
                        "status": status_map.get(status_code, "Inconnu"),
                        "can_request": status_code == 1 
                    }
            return {"tmdb_id": None, "status": "Non trouvé", "can_request": False}
        except Exception as e:
            logger.error(f"Erreur recherche Overseerr ({title}): {e}")
            return {"tmdb_id": None, "status": "Erreur API", "can_request": False}