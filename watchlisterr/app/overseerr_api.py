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

    def get_status(self):
        """Vérifie l'état de santé d'Overseerr."""
        try:
            # L'endpoint /status est parfait pour valider la connexion
            response = requests.get(f"{self.url}/api/v1/status", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "connected": True,
                    "details": response.json()
                }
            elif response.status_code == 401:
                return {"connected": False, "error": "Clé API invalide (401)"}
            else:
                return {"connected": False, "error": f"Erreur HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"Erreur de connexion Overseerr: {e}")
            return {"connected": False, "error": str(e)}
            
    def get_users(self):
        """Récupère la liste des utilisateurs Overseerr ayant un plexId."""
        try:
            # On récupère les utilisateurs (pagination par défaut à 1000 pour être large)
            response = requests.get(
                f"{self.url}/api/v1/user?take=20&skip=0&sort=created", 
                headers=self.headers, 
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # On ne garde que ceux qui ont un plexId (non nul)
            users = []
            for u in data.get('results', []):
                if u.get('plexId'):
                    users.append({
                        "id": u.get('id'),
                        "plexId": u.get('plexId'),
                        "name": u.get('displayName') or u.get('plexUsername')
                    })
            return users
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs : {e}")
            return []