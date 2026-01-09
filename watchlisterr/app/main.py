# 0.3.0 - Reactive Loop + Cycle 1/100
import sys, logging, json, os, time, requests, sqlite3
from threading import Thread
from fastapi import FastAPI
import uvicorn
from overseerr_api import OverseerrClient
from plex_api import PlexClient
from tmdb_api import TMDBClient
from database import Database
from contextlib import asynccontextmanager

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
CYCLE_COUNT = 0

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f: return json.load(f)
    return {}

def run_sync_loop():
    """Boucle principale réactive"""
    global CYCLE_COUNT
    logger.info("🚀 Démarrage de la boucle réactive (Interval: config.yaml)")
    
    while True:
        try:
            opts = get_hass_options()
            interval = opts.get("sync_interval", 3) # En minutes
            
            # 1. Sync Users tous les 100 cycles (ou au cycle 0)
            include_users = (CYCLE_COUNT % 100 == 0)
            
            # 2. Exécution du scan
            run_sync(sync_users=include_users)
            
            # 3. Traitement des requêtes (Simulation)
            if "plex_watchlists" in CACHE:
                ov_client = OverseerrClient(opts.get('overseerr_url'), opts.get('overseerr_api_key'))
                for wl in CACHE["plex_watchlists"]:
                    ov_user_id = db.get_overseerr_id_by_name(wl["name"])
                    if not ov_user_id: continue
                    
                    for item in wl.get("items", []):
                        if item.get("can_request") is True:
                            ov_client.submit_request(
                                tmdb_id=item["tmdb_id"],
                                media_type=item["type"],
                                user_id=ov_user_id,
                                title=item["title"]
                            )

            CYCLE_COUNT += 1
            logger.info(f"💤 Cycle {CYCLE_COUNT} terminé. Prochain scan dans {interval} min.")
            time.sleep(interval * 60)
            
        except Exception as e:
            logger.error(f"💥 Erreur boucle : {e}")
            time.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lancement de la boucle dans un thread séparé
    Thread(target=run_sync_loop, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)
db = Database()

def check_apis(opts):
    """Vérifie l'état des connexions Plex, Overseerr et TMDB"""
    checks = {"plex": "❌ Erreur", "overseerr": "❌ Erreur", "tmdb": "❌ Erreur"}
    
    try:
        p = PlexClient(opts.get('plex_token'), opts.get('plex_server_url'))
        profile = p.get_my_profile()
        if profile: checks["plex"] = f"✅ Connecté ({profile['username']})"
    except Exception: pass

    try:
        url = f"{opts.get('overseerr_url').rstrip('/')}/api/v1/status"
        headers = {"X-Api-Key": opts.get('overseerr_api_key')}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200: checks["overseerr"] = "✅ Connecté"
    except Exception: pass

    try:
        tmdb_key = opts.get('tmdb_api_key')
        r = requests.get(f"https://api.themoviedb.org/3/authentication/token/new?api_key={tmdb_key}", timeout=5)
        if r.status_code == 200: checks["tmdb"] = "✅ Connecté"
    except Exception: pass
    return checks

def sync_users_mapping(plex_client, ov_client):
    """Mapping Plex <> Overseerr basé sur le nom d'utilisateur identique"""
    try:
        logger.info("👥 Synchronisation des mappings utilisateurs...")
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
                logger.info(f"✅ Mapping DB : {p_user['username']} -> ID {match['id']}")
    except Exception as e:
        logger.error(f"Erreur sync_users : {e}")

def run_sync(sync_users=False):
    global CACHE, IS_SCANNING
    if IS_SCANNING: return
    IS_SCANNING = True
    try:
        opts = get_hass_options()
        api_results = check_apis(opts)
        
        ov_client = OverseerrClient(opts.get('overseerr_url'), opts.get('overseerr_api_key'))
        plex_client = PlexClient(opts.get('plex_token'), opts.get('plex_server_url'))
        tmdb_client = TMDBClient(opts.get('tmdb_api_key'))
        
        if sync_users:
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
                match = ov_client.get_media_status(tmdb_id, m_type) if tmdb_id else ov_client.search_content(title, year, m_type)
                
                status = "Déjà présent sur Plex" if server_id else match['status']
                can_req = False if server_id else match.get('can_request', False)

                if status == "Déjà présent sur Plex": stats["already_on_plex"] += 1
                elif can_req: stats["to_overseerr"] += 1

                items_with_status.append({
                    "title": title, "year": year, "type": m_type,
                    "overseerr_status": status, "tmdb_id": tmdb_id, "can_request": can_req
                })
            full_report.append({"name": user['username'], "watchlist_count": len(watchlist), "items": items_with_status})

        stats["total_plex"] = sum(u["watchlist_count"] for u in full_report)
        CACHE = {"status": "Données à jour", "last_update": time.strftime("%Y-%m-%d %H:%M:%S"), "stats": stats, "plex_watchlists": full_report, "api_status": check_apis(opts)}
    except Exception as e:
        logger.error(f"Erreur scan : {e}")
        CACHE["status"] = f"Erreur : {str(e)}"
    finally: IS_SCANNING = False


@app.get("/")
def read_root(): return {"scan_in_progress": IS_SCANNING, "results": CACHE}

@app.get("/sync")
def force_sync():
    if not IS_SCANNING:
        Thread(target=run_sync, kwargs={"sync_users": True}).start()
        return {"message": "Scan forcé lancé (avec users)"}
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