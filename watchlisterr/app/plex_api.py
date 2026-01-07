import requests
import logging
import uuid

logger = logging.getLogger(__name__)

class PlexClient:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "X-Plex-Token": self.token,
            "Accept": "application/json",
            "X-Plex-Client-Identifier": "watchlisterr-ha-addon"
        }

    def get_my_profile(self):
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
        try:
            if not plex_uuid:
                # --- LOGIQUE EXACTE DU CODE SCALA ---
                # URL de base utilisée dans getSelfWatchlist du Scala
                url = "https://discover.provider.plex.tv/library/sections/watchlist/all"
                params = {
                    "X-Plex-Token": self.token,
                    "format": "json", # Important
                    "X-Plex-Container-Start": 0,
                    "X-Plex-Container-Size": 50,
                    "cache_buster": str(uuid.uuid4())[:12] # Comme dans le Scala
                }
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
            else:
                # --- LOGIQUE AMIS ---
                url = "https://community.plex.tv/api"
                query = """
                query GetWatchlistHub($uuid: ID!, $first: PaginationInt!) {
                    user(id: $uuid) {
                        watchlist(first: $first) {
                            nodes { title type year }
                        }
                    }
                }
                """
                variables = {"uuid": plex_uuid, "first": 50}
                response = requests.post(url, headers=self.headers, json={"query": query, "variables": variables}, timeout=15)

            if response.status_code != 200:
                logger.error(f"Plex API Error {response.status_code} sur {'Self' if not plex_uuid else 'Friend'}")
                return []

            data = response.json()
            items = []

            # Parsing pour Self (REST)
            if not plex_uuid:
                # Dans l'API REST, les films sont dans MediaContainer -> Metadata
                metadata = data.get('MediaContainer', {}).get('Metadata', [])
                for item in metadata:
                    items.append({
                        "title": item.get('title'),
                        "type": "movie" if item.get('type') == 'movie' else "tv",
                        "year": item.get('year')
                    })
            # Parsing pour Amis (GraphQL)
            else:
                nodes = data.get('data', {}).get('user', {}).get('watchlist', {}).get('nodes', [])
                for n in nodes:
                    items.append({
                        "title": n.get('title'),
                        "type": "movie" if n.get('type') == 'movie' else "tv",
                        "year": n.get('year')
                    })

            return items
        except Exception as e:
            logger.error(f"Erreur watchlist: {e}")
            return []