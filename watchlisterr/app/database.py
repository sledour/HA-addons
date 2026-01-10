import sqlite3
import logging
import sys
from datetime import datetime

logger = logging.getLogger("watchlisterr")

class Database:
    def __init__(self, db_path="/data/watchlisterr.db"):
        self.db_path = db_path
        self.create_tables()

    def create_tables(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # --- LIGNE TEMPORAIRE POUR FORCER LA MISE À JOUR ---
                # Supprime cette ligne après le prochain redémarrage réussi
                cursor.execute("DROP TABLE IF EXISTS media_cache")
                # ---------------------------------------------------
                
                # --- CRÉATION DES TABLES PROPRES ---
                
                # Table des utilisateurs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        plex_id TEXT PRIMARY KEY,
                        username TEXT,
                        overseerr_id INTEGER,
                        role TEXT
                    )
                ''')

                # Table Cache Média
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS media_cache (
                        tmdb_id INTEGER PRIMARY KEY,
                        title TEXT,
                        media_type TEXT,
                        year INTEGER,
                        poster_path TEXT,
                        on_server INTEGER DEFAULT 0,
                        added_at DATETIME
                    )
                ''')
                
                conn.commit()
                logger.info("✅ Base de données SQLite initialisée avec succès.")
                
        except Exception as e:
            logger.error(f"❌ Erreur initialisation SQLite: {e}")

    def save_user(self, plex_id, username, overseerr_id, role):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (plex_id, username, overseerr_id, role)
                VALUES (?, ?, ?, ?)
            ''', (plex_id, username, overseerr_id, role))
            conn.commit()

    def get_overseerr_id_by_name(self, username):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT overseerr_id FROM users WHERE LOWER(username) = LOWER(?)', (username,))
            row = cursor.fetchone()
            return row[0] if row else None

    def save_media(self, tmdb_id, title, media_type, year, poster_path, on_server=0):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO media_cache 
                (tmdb_id, title, media_type, year, poster_path, on_server, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (tmdb_id, title, media_type, year, poster_path, on_server, datetime.now()))
            conn.commit()

    def get_cached_media(self, title, year):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM media_cache 
                WHERE LOWER(title) = LOWER(?) AND year = ?
            ''', (title, year))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_users(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            return [dict(row) for row in cursor.fetchall()]

    def get_all_media(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM media_cache ORDER BY added_at DESC')
            return [dict(row) for row in cursor.fetchall()]

    def clear_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM media_cache')
            cursor.execute('DELETE FROM users')
            conn.commit()