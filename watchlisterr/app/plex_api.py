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
        """Récupère l'UUID du compte principal."""
        url = "https://plex.tv/users/account.json"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json().get('user', {})
                return {
                    "plex_id": user_data.get('uuid'),
                    "username": user_data.get('username')
                }
            return None
        except Exception as e:
            logger.error(f"Erreur Profil: {e}")
            return None

    def get_friends(self):
        """Récupère la liste des amis."""
        query = {"query": "query GetAllFriends { allFriendsV2 { user { id username } } }"}
        try:
            response = requests.post(self.url, headers=self.headers, json=query, timeout=15)
            data = response.json()
            friends = []
            for entry in data.get('data', {}).get('allFriendsV2', []):
                u = entry.get('user', {})
                friends.append({"plex_id": u.get('id'), "username": u.get('username')})
            return friends
        except Exception as e:
            logger.error(f"Erreur Friends: {e}")
            return None

    def get_watchlist(self, plex_uuid):
        """Récupère la watchlist d'un utilisateur (soi-même ou ami)."""
        query = {
            "query": """
                query GetWatchlist($userId: ID!) {
                    watchlistV2(userId: $userId, first: 20) {
                        nodes {
                            title
                            type
                            year
                        }
                    }
                }
            """,
            "variables": {"userId": plex_uuid}
        }
        try:
            response = requests.post(self.url, headers=self.headers, json=query, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('watchlistV2', {}).get('nodes', [])
        except Exception as e:
            logger.error(f"Erreur Watchlist pour {plex_uuid}: {e}")
            return []