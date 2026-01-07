import requests
import logging

logger = logging.getLogger(__name__)

class OverseerrClient:
    def __init__(self, url, api_key):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def test_connection(self):
        """Vérifie si l'URL et la clé API sont valides."""
        try:
            response = requests.get(f"{self.url}/api/v1/status", headers=self.headers, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erreur connexion Overseerr: {e}")
            return False

    def get_users_mapping(self):
        """Récupère la liste des utilisateurs et retourne un mapping simplifié."""
        try:
            response = requests.get(f"{self.url}/api/v1/user", headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            mapping = []
            for user in data.get('results', []):
                mapping.append({
                    "overseerr_id": user.get('id'),
                    "plex_id": user.get('plexId'),
                    "name": user.get('displayName') or user.get('plexUsername')
                })
            return mapping
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            return None