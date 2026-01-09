# 0.3.0 - Stable with DB
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger("watchlisterr")

class Database:
    def __init__(self, db_path="/data/watchlisterr.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        plex_uuid TEXT PRIMARY KEY,
                        username TEXT,
                        overseerr_id INTEGER,
                        role TEXT
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS media_cache (
                        tmdb_id INTEGER PRIMARY KEY,
                        title TEXT,
                        media_type TEXT,
                        year INTEGER
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS media_cache (
                        tmdb_id INTEGER PRIMARY KEY,
                        title TEXT,
                        type TEXT,
                        poster_path TEXT,
                        added_at DATETIME
                    )
                ''')
                conn.commit()
                logger.info("✅ Base de données SQLite initialisée avec succès.")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation SQLite: {e}")

    def save_user(self, plex_uuid, username, overseerr_id, role):
        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO users (plex_uuid, username, overseerr_id, role)
                VALUES (?, ?, ?, ?)
            ''', (plex_uuid, username, overseerr_id, role))

    def get_overseerr_id_by_name(self, username):
        """Récupère l'ID Overseerr via le nom d'utilisateur (pour le scan réactif)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT overseerr_id FROM users WHERE username = ?", (username,))
            res = cursor.fetchone()
            return res[0] if res else None

    def get_cached_media(self, title, year):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM media_cache WHERE title = ? AND year = ?", (title, year))
            res = cursor.fetchone()
            return dict(res) if res else None

    def save_media(self, tmdb_id, title, media_type, year, poster_path):
        query = """
            INSERT OR REPLACE INTO media (tmdb_id, title, media_type, year, poster_path, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (tmdb_id, title, media_type, year, poster_path, datetime.now()))
        self.conn.commit()

    def setup_db(self):
        # Ajoute poster_path à ta structure de table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS media (
                tmdb_id INTEGER PRIMARY KEY,
                title TEXT,
                media_type TEXT,
                year INTEGER,
                poster_path TEXT,
                last_updated DATETIME
            )
        ''')