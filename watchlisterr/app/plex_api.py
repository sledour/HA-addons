# Stable version 0.1.0
import requests
import logging

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
        """Récupère ton profil (Admin)"""
        try:
            response = requests.get("https://plex.tv/users/account.json", headers=self.headers, timeout=10)
            if response.status_code == 200:
                user = response.json().get('user', {})
                return {"plex_id": user.get('uuid'), "username": user.get('username')}
            return None
        except Exception as e:
            logger.error(f"Erreur profil Plex: {e}")
            return None

    def get_friends(self):
        """Récupère la liste de tes amis Plex via l'API GraphQL"""
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
            logger.error(f"Erreur récupération amis Plex: {e}")
            return []

    def extract_tmdb_id(self, guid_list):
        """Extrait l'ID TMDB d'une liste de GUIDs (format standard)"""
        if not guid_list: return None
        for g in guid_list:
            id_val = g.get('id', '')
            if id_val.startswith('tmdb://'):
                try:
                    return int(id_val.split('://')[1])
                except (IndexError, ValueError): continue
        return None

    def parse_guid_string(self, guid_string):
        """Extrait l'ID TMDB d'une chaîne GUID (format GraphQL des amis)"""
        if guid_string and 'tmdb://' in guid_string:
            try:
                # guid est souvent 'plex://movie/5d77682...|tmdb://12345'
                parts = guid_string.split('tmdb://')
                if len(parts) > 1:
                    return int(parts[1].split('|')[0].split('/')[0])
            except Exception: pass
        return None

    def find_tmdb_id_on_server(self, title, year, media_type):
        """Vérifie si le film est physiquement présent sur ton serveur Plex"""
        if not self.server_url: return None
        try:
            url = f"{self.server_url}/library/all"
            # On convertit le type pour la recherche serveur
            p_type = 2 if media_type in ["show", "tv"] else 1
            params = {"title": title, "type": p_type, "X-Plex-Token": self.token}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                metadata = response.json().get('MediaContainer', {}).get('Metadata', [])
                for item in metadata:
                    item_year = item.get('year')
                    if not year or not item_year or str(item_year) == str(year):
                        return self.extract_tmdb_id(item.get('Guid', []))
            return None
        except Exception: return None

    def get_watchlist(self, plex_uuid=None):
        """Récupère la watchlist (Admin ou Ami)"""
        try:
            if not plex_uuid:
                # Version ADMIN (API Discover)
                url = "https://discover.provider.plex.tv/library/sections/watchlist/all"
                params = {"X-Plex-Token": self.token, "format": "json"}
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                metadata = response.json().get('MediaContainer', {}).get('Metadata', [])
                return [{
                    "title": i.get('title'), 
                    "type": "tv" if i.get('type') in ["show","series","tv"] else "movie", 
                    "year": i.get('year'), 
                    "tmdb_id": self.extract_tmdb_id(i.get('Guid', []))
                } for i in metadata]
            else:
                # Version AMI (API GraphQL)
                url = "https://community.plex.tv/api"
                query = """query GetWatchlist($uuid: ID!, $first: PaginationInt!) { 
                    user(id: $uuid) { watchlist(first: $first) { nodes { title type year guid } } } 
                }"""
                vars = {"uuid": plex_uuid, "first": 100}
                response = requests.post(url, headers=self.headers, json={"query": query, "variables": vars}, timeout=15)
                nodes = response.json().get('data', {}).get('user', {}).get('watchlist', {}).get('nodes', [])
                
                watchlist = []
                for n in nodes:
                    watchlist.append({
                        "title": n.get('title'), 
                        "type": "tv" if n.get('type') in ["show","series","tv"] else "movie", 
                        "year": n.get('year'), 
                        # ICI: On extrait enfin l'ID TMDB au lieu de mettre None
                        "tmdb_id": self.parse_guid_string(n.get('guid'))
                    })
                return watchlist
        except Exception as e:
            logger.error(f"Erreur watchlist Plex pour {plex_uuid}: {e}")
            return []