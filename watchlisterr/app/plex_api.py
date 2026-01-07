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