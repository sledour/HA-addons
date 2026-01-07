import requests
import logging
import uuid

logger = logging.getLogger(__name__)

class PlexClient:
    def __init__(self, token, server_url=None):
        self.token = token
        self.server_url = server_url.rstrip('/') if server_url else None
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

    def extract_tmdb_id(self, guid_list):
        """Extrait l'ID TMDB depuis une liste de guids (Plex JSON format)"""
        if not guid_list: return None
        for g in guid_list:
            id_val = g.get('id', '')
            if id_val.startswith('tmdb://'):
                try:
                    return int(id_val.split('://')[1])
                except (IndexError, ValueError):
                    continue
        return None

    def find_tmdb_id_on_server(self, title, year):
        """
        Cherche un contenu sur ton serveur distant pour extraire son ID TMDB.
        Sert de base de référence pour les watchlists des amis.
        """
        if not self.server_url:
            return None
            
        try:
            # On cherche dans toutes les bibliothèques
            url = f"{self.server_url}/library/all"
            params = {
                "title": title,
                "X-Plex-Token": self.token
            }
            # Note: On ne filtre pas par année dans les params car Plex est parfois capricieux 
            # sur le format. On filtrera manuellement après.
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                metadata = response.json().get('MediaContainer', {}).get('Metadata', [])
                for item in metadata:
                    # Vérification de l'année pour éviter les faux positifs (ex: version 1998 vs 2024)
                    item_year = item.get('year')
                    if not year or not item_year or str(item_year) == str(year):
                        return self.extract_tmdb_id(item.get('Guid', []))
            return None
        except Exception as e:
            logger.debug(f"Recherche serveur local échouée pour {title}: {e}")
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
                    "X-Plex-Container-Size": 100,
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
                                guid
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
                    raw_type = item.get('type', '').lower()
                    clean_type = "tv" if raw_type in ["show", "series", "tv", "2"] else "movie"
                    tmdb_id = self.extract_tmdb_id(item.get('Guid', []))
                    
                    items.append({
                        "title": item.get('title'),
                        "type": clean_type,
                        "year": item.get('year'),
                        "tmdb_id": tmdb_id
                    })
            else:
                nodes = data.get('data', {}).get('user', {}).get('watchlist', {}).get('nodes', [])
                for n in nodes:
                    raw_type = n.get('type', '').lower()
                    clean_type = "tv" if raw_type in ["show", "series", "tv", "season", "episode"] else "movie"
                    
                    items.append({
                        "title": n.get('title'),
                        "type": clean_type,
                        "year": n.get('year'),
                        "tmdb_id": None # Sera éventuellement cherché sur le serveur par main.py
                    })

            return items
        except Exception as e:
            logger.error(f"Erreur watchlist: {e}")
            return []