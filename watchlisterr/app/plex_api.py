import requests
import logging

logger = logging.getLogger(__name__)

class PlexClient:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "X-Plex-Token": self.token,
            "Accept": "application/json"
        }

    def get_my_profile(self):
        """Récupère l'UUID via plex.tv/users/account."""
        try:
            response = requests.get("https://plex.tv/users/account.json", headers=self.headers, timeout=10)
            if response.status_code == 200:
                user = response.json().get('user', {})
                return {"plex_id": user.get('uuid'), "username": user.get('username')}
            return None
        except Exception as e:
            logger.error(f"Erreur profil: {e}")
            return None

    def get_friends(self):
        """Récupère les amis via GraphQL (copié du Scala)."""
        url = "https://community.plex.tv/api"
        query = {"query": "query GetAllFriends { allFriendsV2 { user { id username } } }"}
        try:
            response = requests.post(url, headers=self.headers, json=query, timeout=15)
            data = response.json()
            friends = []
            for entry in data.get('data', {}).get('allFriendsV2', []):
                u = entry.get('user', {})
                friends.append({"plex_id": u.get('id'), "username": u.get('username')})
            return friends
        except Exception as e:
            logger.error(f"Erreur amis: {e}")
            return None

    def get_watchlist(self, plex_uuid=None):
        """Logique hybride du Scala."""
        try:
            if not plex_uuid:
                # 1. TA WATCHLIST (discover.provider.plex.tv)
                url = "https://discover.provider.plex.tv/library/sections/watchlist/all"
                params = {
                    "X-Plex-Token": self.token,
                    "X-Plex-Container-Start": 0,
                    "X-Plex-Container-Size": 50
                }
                response = requests.get(url, params=params, timeout=15)
            else:
                # 2. WATCHLIST AMIS (GraphQL imbriqué)
                url = "https://community.plex.tv/api"
                query = """
                query GetWatchlistHub($uuid: ID!, $first: PaginationInt!) {
                    user(id: $uuid) {
                        watchlist(first: $first) {
                            nodes {
                                title
                                type
                            }
                        }
                    }
                }
                """
                variables = {"uuid": plex_uuid, "first": 50}
                response = requests.post(url, headers=self.headers, json={"query": query, "variables": variables}, timeout=15)
            
            response.raise_for_status()
            data = response.json()
            
            items = []
            if not plex_uuid:
                # Format REST (Self)
                metadata = data.get('MediaContainer', {}).get('Metadata', [])
                for item in metadata:
                    items.append({"title": item.get('title'), "type": item.get('type')})
            else:
                # Format GraphQL (Friend)
                nodes = data.get('data', {}).get('user', {}).get('watchlist', {}).get('nodes', [])
                for n in nodes:
                    items.append({"title": n.get('title'), "type": n.get('type')})
            
            return items
        except Exception as e:
            logger.error(f"Erreur watchlist: {e}")
            return []