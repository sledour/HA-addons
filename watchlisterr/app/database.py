# 0.3.0 - Stable with DB
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger("watchlisterr")

class Database:
    def __init__(self, db_path="/data/watchlisterr.db"):
        self.db_path = db_path
        self._create_tables()
        # On crée la connexion et le curseur dès l'initialisation
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
        self.cursor = self.conn.cursor()
        self.setup_db()

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
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # On utilise LOWER pour ignorer la casse et CAST pour être sûr de l'année
        query = "SELECT * FROM media WHERE LOWER(title) = LOWER(?) AND CAST(year AS TEXT) = CAST(? AS TEXT)"
        cursor.execute(query, (title, year))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def save_media(self, tmdb_id, title, media_type, year, poster_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # INSERT OR REPLACE permet de mettre à jour le poster si le film existe déjà
        query = """
            INSERT OR REPLACE INTO media (tmdb_id, title, media_type, year, poster_path)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (tmdb_id, title, media_type, year, poster_path))
        conn.commit()
        conn.close()

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

    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_all_media(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM media ORDER BY title ASC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows