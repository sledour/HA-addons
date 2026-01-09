import sqlite3
import logging

logger = logging.getLogger("watchlisterr")

class Database:
    def __init__(self, db_path="/data/watchlisterr.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Table des utilisateurs (Plex UUID <-> Overseerr ID)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    plex_uuid TEXT PRIMARY KEY,
                    username TEXT,
                    overseerr_id INTEGER,
                    role TEXT
                )
            ''')
            # Table Cache Media (TMDB ID, Type corrigé)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS media_cache (
                    tmdb_id INTEGER PRIMARY KEY,
                    title TEXT,
                    media_type TEXT,
                    year INTEGER
                )
            ''')
            conn.commit()

    # --- Gestion Users ---
    def save_user(self, plex_uuid, username, overseerr_id, role):
        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO users (plex_uuid, username, overseerr_id, role)
                VALUES (?, ?, ?, ?)
            ''', (plex_uuid, username, overseerr_id, role))

    def get_overseerr_id(self, plex_uuid):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT overseerr_id FROM users WHERE plex_uuid = ?", (plex_uuid,))
            res = cursor.fetchone()
            return res[0] if res else None

    # --- Gestion Cache Media ---
    def get_cached_media(self, title, year):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM media_cache WHERE title = ? AND year = ?", (title, year))
            res = cursor.fetchone()
            return dict(res) if res else None

    def save_media(self, tmdb_id, title, media_type, year):
        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR IGNORE INTO media_cache (tmdb_id, title, media_type, year)
                VALUES (?, ?, ?, ?)
            ''', (tmdb_id, title, media_type, year))