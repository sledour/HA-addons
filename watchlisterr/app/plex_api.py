import requests
import logging

logger = logging.getLogger(__name__)

class PlexClient:
    def __init__(self, token):
        self.token = token
        self.url = "https://community.plex.tv/api"
        self.headers = {
            "X-Plex-Token": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    def get_my_profile(self):
        """Récupère les infos du compte principal via plex.tv/users/account."""
        url = "https://plex.tv/users/account.json"
        try:
            # On utilise le même token
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                # Note: On récupère l'UUID (id) et le username
                return {
                    "plex_id": user_data.get('uuid') or user_data.get('id'),
                    "username": user_data.get('username')
                }
            else:
                logger.error(f"Erreur Profil Plex.tv: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Exception Profil Plex.tv: {e}")
            return None
        
    def get_friends(self):
        """Récupère la liste des amis Plex (ID et Username)."""
        query = {
            "query": """
                query GetAllFriends {
                    allFriendsV2 {
                        user {
                            id
                            username
                        }
                    }
                }
            """
        }
        try:
            response = requests.post(self.url, headers=self.headers, json=query, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            friends = []
            friends_list = data.get('data', {}).get('allFriendsV2', [])
            
            for entry in friends_list:
                user = entry.get('user', {})
                if user.get('id'):
                    friends.append({
                        "plex_id": user.get('id'),
                        "username": user.get('username')
                    })
            return friends
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des amis Plex: {e}")
            return None