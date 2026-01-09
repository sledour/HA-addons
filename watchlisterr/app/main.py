import sys, logging, json, os, time, requests, sqlite3
from threading import Thread
from fastapi import FastAPI
import uvicorn
from overseerr_api import OverseerrClient
from plex_api import PlexClient
from tmdb_api import TMDBClient
from database import Database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
sys.stdout.reconfigure(line_buffering=True)
logger = logging.getLogger("watchlisterr")

CACHE = {
    "status": "Initialisation...", 
    "last_update": None, 
    "stats": {}, 
    "plex_watchlists": [],
    "api_status": {"plex": "Attente...", "overseerr": "Attente...", "tmdb": "Attente..."}
}
IS_SCANNING = False

app = FastAPI()
db = Database()

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f: return json.load(f)
    return {}

def check_apis(opts):
    """Vérifie l'état des connexions Plex, Overseerr et TMDB"""
    checks = {"plex": "❌ Erreur", "overseerr": "❌ Erreur", "tmdb": "❌ Erreur"}
    
    try:
        p = PlexClient(opts.get('plex_token'), opts.get('plex_server_url'))
        profile = p.get_my_profile()
        if profile:
            checks["plex"] = f"✅ Connecté ({profile['username']})"
            logger.info(f"[CHECK] Plex: OK (User: {profile['username']})")
    except Exception as e:
        checks["plex"] = f"❌ Erreur: {str(e)}"

    try:
        url = f"{opts.get('overseerr_url').rstrip('/')}/api/v1/status"
        headers = {"X-Api-Key": opts.get('overseerr_api_key')}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            checks["overseerr"] = "✅ Connecté"
            logger.info("[CHECK] Overseerr: OK")
    except Exception as e:
        checks["overseerr"] = f"❌ Erreur: {str(e)}"

    try:
        tmdb_key = opts.get('tmdb_api_key')
        r = requests.get(f"https://api.themoviedb.org/3/authentication/token/new?api_key={tmdb_key}", timeout=5)
        if r.status_code in [200, 401]:
            if r.status_code == 200:
                checks["tmdb"] = "✅ Connecté"
                logger.info("[CHECK] TMDB: OK")
            else:
                checks["tmdb"] = "❌ Clé API Invalide"
    except Exception as e:
        checks["tmdb"] = f"❌ Erreur: {str(e)}"
    
    return checks

def sync_users_mapping(plex_client, ov_client):
    """Mapping Plex <> Overseerr basé sur le nom d'utilisateur identique"""
    try:
        logger.info("Synchronisation des mappings utilisateurs...")
        plex_users = []
        admin = plex_client.get_my_profile()
        if admin: plex_users.append({**admin, "role": "Admin"})
        
        friends = plex_client.get_friends() or []
        for f in friends: plex_users.append({**f, "role": "Friend"})
        
        ov_users = ov_client.get_users()
        
        for p_user in plex_users:
            match = next((u for u in ov_users if u['displayName'].lower() == p_user['username'].lower()), None)
            if match:
                db.save_user(p_user['plex_id'], p_user['username'], match['id'], p_user['role'])
                logger.info(f"✅ Mapping : {p_user['username']} -> Overseerr ID {match['id']}")
            else:
                logger.warning(f"⚠️ Aucun compte Overseerr pour {p_user['username']}")
    except Exception as e:
        logger.error(f"Erreur sync_users : {e}")

def run_sync():
    global CACHE, IS_SCANNING
    if IS_SCANNING: return
    IS_SCANNING = True
    try:
        opts = get_hass_options()
        api_results = check_apis(opts)
        
        ov_client = OverseerrClient(opts.get('overseerr_url'), opts.get('overseerr_api_key'))
        plex_client = PlexClient(opts.get('plex_token'), opts.get('plex_server_url'))
        tmdb_client = TMDBClient(opts.get('tmdb_api_key'))
        
        sync_users_mapping(plex_client, ov_client)
        
        logger.info("Début du scan complet...")
        my_profile = plex_client.get_my_profile()
        friends = plex_client.get_friends() or []
        
        users_to_process = []
        if my_profile: users_to_process.append({"plex_id": None, "username": my_profile['username'], "role": "Admin"})
        for f in friends: users_to_process.append({"plex_id": f['plex_id'], "username": f['username'], "role": "Friend"})

        full_report = []
        stats = {"total_plex": 0, "already_on_plex": 0, "to_overseerr": 0}

        for user in users_to_process:
            watchlist = plex_client.get_watchlist(user['plex_id'])
            items_with_status = []
            
            for item in watchlist:
                title, year, m_type = item['title'], item['year'], item['type']
                tmdb_id = item.get('tmdb_id')

                if not tmdb_id:
                    cached = db.get_cached_media(title, year)
                    if cached:
                        tmdb_id, m_type = cached['tmdb_id'], cached['media_type']
                    else:
                        tmdb_res = tmdb_client.search_multi(title, year)
                        if tmdb_res:
                            tmdb_id, m_type = tmdb_res['tmdb_id'], tmdb_res['type']
                            db.save_media(tmdb_id, title, m_type, year)
                            logger.info(f"🆕 TMDB mis en cache : {title} ({tmdb_id})")

                server_id = plex_client.find_tmdb_id_on_server(title, year, m_type)
                
                if tmdb_id:
                    match = ov_client.get_media_status(tmdb_id, m_type)
                else:
                    match = ov_client.search_content(title, year, m_type)
                
                status = "Déjà présent sur Plex" if server_id else match['status']
                can_req = False if server_id else match.get('can_request', False)

                if status == "Déjà présent sur Plex": stats["already_on_plex"] += 1
                elif can_req: stats["to_overseerr"] += 1

                items_with_status.append({
                    "title": title, "year": year, "type": m_type,
                    "overseerr_status": status, "tmdb_id": tmdb_id, "can_request": can_req
                })
            
            full_report.append({"name": user['username'], "type": user['role'], "watchlist_count": len(watchlist), "items": items_with_status})

        stats["total_plex"] = sum(u["watchlist_count"] for u in full_report)
        CACHE = {"status": "Données à jour", "last_update": time.strftime("%Y-%m-%d %H:%M:%S"), "stats": stats, "plex_watchlists": full_report, "api_status": api_results}
        logger.info(f"Scan terminé : {stats['total_plex']} items traités.")

        # --- AJOUT : RAPPORT DE BASE DE DONNÉES ---
        with db._get_connection() as conn:
            user_count = conn.execute("SELECT count(*) FROM users").fetchone()[0]
            cache_count = conn.execute("SELECT count(*) FROM media_cache").fetchone()[0]
            logger.info(f"📊 [DATABASE] État de la base : {user_count} utilisateurs mappés, {cache_count} médias en cache.")
            
            # Optionnel : Lister les noms des users en DB pour confirmer
            users = conn.execute("SELECT username FROM users").fetchall()
            user_list = ", ".join([u[0] for u in users])
            logger.info(f"👥 [DATABASE] Utilisateurs en base : {user_list}")
        # ------------------------------------------

    except Exception as e:
        logger.error(f"Erreur scan : {e}")
        CACHE["status"] = f"Erreur : {str(e)}"
    finally: IS_SCANNING = False

@app.on_event("startup")
def startup_event(): Thread(target=run_sync).start()

@app.get("/")
def read_root(): return {"scan_in_progress": IS_SCANNING, "results": CACHE}

@app.get("/sync")
def force_sync():
    if not IS_SCANNING:
        Thread(target=run_sync).start()
        return {"message": "Scan lancé"}
    return {"message": "Déjà en cours"}

@app.get("/debug/users")
def debug_users():
    with db._get_connection() as conn:
        conn.row_factory = sqlite3.Row
        res = conn.execute("SELECT * FROM users").fetchall()
        return [dict(row) for row in res]

@app.get("/debug/cache")
def debug_cache():
    with db._get_connection() as conn:
        conn.row_factory = sqlite3.Row
        res = conn.execute("SELECT * FROM media_cache").fetchall()
        return [dict(row) for row in res]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1604)