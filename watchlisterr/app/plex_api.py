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
        if not guid_list: return None
        for g in guid_list:
            id_val = g.get('id', '')
            if id_val.startswith('tmdb://'):
                try:
                    return int(id_val.split('://')[1])
                except (IndexError, ValueError): continue
        return None

    def find_tmdb_id_on_server(self, title, year, media_type):
        if not self.server_url: return None
        try:
            url = f"{self.server_url}/library/all"
            params = {"title": title, "X-Plex-Token": self.token}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                metadata = response.json().get('MediaContainer', {}).get('Metadata', [])
                for item in metadata:
                    raw_type = item.get('type', '').lower()
                    current_type = "tv" if raw_type in ["show", "series"] else "movie"
                    if current_type == media_type:
                        item_year = item.get('year')
                        if not year or not item_year or str(item_year) == str(year):
                            return self.extract_tmdb_id(item.get('Guid', []))
            return None
        except Exception: return None

    def get_watchlist(self, plex_uuid=None):
        try:
            if not plex_uuid:
                url = "https://discover.provider.plex.tv/library/sections/watchlist/all"
                params = {"X-Plex-Token": self.token, "format": "json"}
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                metadata = response.json().get('MediaContainer', {}).get('Metadata', [])
                return [{"title": i.get('title'), "type": "tv" if i.get('type') in ["show","series","tv"] else "movie", 
                         "year": i.get('year'), "tmdb_id": self.extract_tmdb_id(i.get('Guid', []))} for i in metadata]
            else:
                url = "https://community.plex.tv/api"
                query = """query GetWatchlist($uuid: ID!, $first: PaginationInt!) { 
                    user(id: $uuid) { watchlist(first: $first) { nodes { title type year guid } } } 
                }"""
                vars = {"uuid": plex_uuid, "first": 100}
                response = requests.post(url, headers=self.headers, json={"query": query, "variables": vars}, timeout=15)
                nodes = response.json().get('data', {}).get('user', {}).get('watchlist', {}).get('nodes', [])
                return [{"title": n.get('title'), "type": "tv" if n.get('type') in ["show","series","tv"] else "movie", 
                         "year": n.get('year'), "tmdb_id": None} for n in nodes]
        except Exception as e:
            logger.error(f"Erreur watchlist: {e}")
            return []