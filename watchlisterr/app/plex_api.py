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
                # --- LOGIQUE SOI (REST) ---
                url = "https://discover.provider.plex.tv/library/sections/watchlist/all"
                params = {
                    "X-Plex-Token": self.token,
                    "format": "json",
                    "X-Plex-Container-Start": 0,
                    "X-Plex-Container-Size": 100, # Augmenté pour être large
                    "cache_buster": str(uuid.uuid4())[:12]
                }
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
            else:
                # --- LOGIQUE AMIS (GraphQL) ---
                url = "https://community.plex.tv/api"
                query = """
                query GetWatchlistHub($uuid: ID!, $first: PaginationInt!) {
                    user(id: $uuid) {
                        watchlist(first: $first) {
                            nodes { 
                                title 
                                type 
                                year 
                            }
                        }
                    }
                }
                """
                variables = {"uuid": plex_uuid, "first": 100}
                response = requests.post(url, headers=self.headers, json={"query": query, "variables": variables}, timeout=15)

            if response.status_code != 200:
                logger.error(f"Plex API Error {response.status_code}")
                return []

            data = response.json()
            items = []

            if not plex_uuid:
                metadata = data.get('MediaContainer', {}).get('Metadata', [])
                for item in metadata:
                    # Normalisation du type pour Overseerr
                    raw_type = item.get('type')
                    clean_type = "movie" if raw_type == "movie" else "tv"
                    
                    items.append({
                        "title": item.get('title'),
                        "type": clean_type,
                        "year": item.get('year')
                    })
            else:
                nodes = data.get('data', {}).get('user', {}).get('watchlist', {}).get('nodes', [])
                for n in nodes:
                    # IMPORTANT : En GraphQL, les séries sont souvent de type 'show'
                    raw_type = n.get('type')
                    clean_type = "movie" if raw_type == "movie" else "tv"
                    
                    items.append({
                        "title": n.get('title'),
                        "type": clean_type,
                        "year": n.get('year')
                    })

            return items
        except Exception as e:
            logger.error(f"Erreur watchlist: {e}")
            return []