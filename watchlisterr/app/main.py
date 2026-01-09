# 0.3.5 - UI Dashboard Full Sync + Fix Posters & Names + Detailed Logs
import sys, logging, json, os, time, requests, sqlite3, collections
from threading import Thread
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from overseerr_api import OverseerrClient
from plex_api import PlexClient
from tmdb_api import TMDBClient
from database import Database

# --- CONFIGURATION LOGS (MATRIX STYLE) ---
LOG_HISTORY = collections.deque(maxlen=20)

class UIHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "msg": self.format(record)
        }
        LOG_HISTORY.append(log_entry)

logger = logging.getLogger("watchlisterr")
logger.setLevel(logging.INFO)
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(sh)
logger.addHandler(UIHandler())

# --- INITIALISATION ---
CACHE = {
    "status": "Initialisation...", 
    "last_update": None, 
    "stats": {"to_overseerr": 0}, 
    "plex_watchlists": [],
    "api_status": {"plex": "Attente...", "overseerr": "Attente...", "tmdb": "Attente..."}
}
IS_SCANNING = False
CYCLE_COUNT = 0

db = Database()
templates = Jinja2Templates(directory="/app/templates")

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f: return json.load(f)
    return {}

# --- FONCTION DE VÉRIFICATION DES APIS ---
def check_apis(opts):
    """Vérifie l'état des connexions Plex, Overseerr et TMDB"""
    checks = {"plex": "❌ Erreur", "overseerr": "❌ Erreur", "tmdb": "❌ Erreur"}
    
    try:
        p = PlexClient(opts.get('plex_token'), opts.get('plex_url')) # Correction plex_url
        profile = p.get_my_profile()
        if profile:
            checks["plex"] = f"✅ Connecté ({profile['username']})"
            logger.info(f"[CHECK] Plex: OK (User: {profile['username']})")
    except Exception as e:
        logger.error(f"[CHECK] Plex: HS -> {e}")

    try:
        url = f"{opts.get('overseerr_url').rstrip('/')}/api/v1/status"
        headers = {"X-Api-Key": opts.get('overseerr_api_key')}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            checks["overseerr"] = "✅ Connecté"
            logger.info("[CHECK] Overseerr: OK")
    except Exception as e:
        logger.error(f"[CHECK] Overseerr: HS -> {e}")

    try:
        tmdb_key = opts.get('tmdb_api_key')
        r = requests.get(f"https://api.themoviedb.org/3/authentication/token/new?api_key={tmdb_key}", timeout=5)
        if r.status_code in [200, 401]:
            checks["tmdb"] = "✅ Connecté" if r.status_code == 200 else "❌ Clé Invalide"
            logger.info(f"[CHECK] TMDB: {'OK' if r.status_code == 200 else 'Clé Invalide'}")
    except Exception as e:
        logger.error(f"[CHECK] TMDB: HS -> {e}")
    
    CACHE["api_status"] = checks
    return checks

# --- LOGIQUE DE SYNCHRONISATION ---

def run_sync_loop():
    global CYCLE_COUNT
    logger.info("🚀 Démarrage de la boucle réactive")
    while True:
        try:
            opts = get_hass_options()
            interval = opts.get("sync_interval", 3)
            is_dry_run = opts.get("dry_run", True)
            
            check_apis(opts)
            run_sync(sync_users=(CYCLE_COUNT % 100 == 0))
            
            if "plex_watchlists" in CACHE:
                ov_client = OverseerrClient(opts.get('overseerr_url'), opts.get('overseerr_api_key'))
                for wl in CACHE["plex_watchlists"]:
                    ov_user_id = db.get_overseerr_id_by_name(wl["name"])
                    if not ov_user_id: continue
                    for item in wl.get("items", []):
                        if item.get("can_request") is True:
                            logger.info(f"📤 Requête pour {item['title']} ({wl['name']})")
                            ov_client.submit_request(
                                tmdb_id=item["tmdb_id"],
                                media_type=item["type"],
                                user_id=ov_user_id,
                                title=item["title"],
                                is_simulation=is_dry_run
                            )

            CYCLE_COUNT += 1
            logger.info(f"💤 Cycle {CYCLE_COUNT} terminé. Attente {interval} min.")
            time.sleep(interval * 60)
        except Exception as e:
            logger.error(f"💥 Erreur boucle : {e}")
            time.sleep(60)

def run_sync(sync_users=False):
    global CACHE, IS_SCANNING
    if IS_SCANNING: return
    IS_SCANNING = True
    try:
        opts = get_hass_options()
        ov_client = OverseerrClient(opts.get('overseerr_url'), opts.get('overseerr_api_key'))
        plex_client = PlexClient(opts.get('plex_token'), opts.get('plex_url'))
        tmdb_client = TMDBClient(opts.get('tmdb_api_key'))
        
        if sync_users:
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
                    logger.info(f"✅ User mappé : {p_user['username']} -> {match['id']}")

        logger.info("🔍 Scan des Watchlists en cours...")
        my_profile = plex_client.get_my_profile()
        friends = plex_client.get_friends() or []
        
        users_to_process = []
        if my_profile: users_to_process.append({"plex_id": None, "username": my_profile['username']})
        for f in friends: users_to_process.append({"plex_id": f['plex_id'], "username": f['username']})
        
        full_report = []
        total_items = 0
        for user in users_to_process:
            watchlist = plex_client.get_watchlist(user['plex_id'])
            logger.info(f"👤 Traitement de : {user['username']} ({len(watchlist)} médias)")
            items_with_status = []
            for item in watchlist:
                total_items += 1
                tmdb_id, m_type, poster = None, item['type'], None
                cached = db.get_cached_media(item['title'], item['year'])
                
                if cached:
                    tmdb_id, m_type, poster = cached['tmdb_id'], cached['media_type'], cached.get('poster_path')
                else:
                    tmdb_res = tmdb_client.search_multi(item['title'], item['year'])
                    if tmdb_res:
                        tmdb_id, m_type, poster = tmdb_res['tmdb_id'], tmdb_res['type'], tmdb_res.get('poster_path')
                        db.save_media(tmdb_id, item['title'], m_type, item['year'], poster)
                        logger.info(f"🆕 TMDB mis en cache : {item['title']}")
                
                match = ov_client.get_media_status(tmdb_id, m_type) if tmdb_id else {'status': 'Inconnu', 'can_request': False}
                
                items_with_status.append({
                    "title": item['title'], "type": m_type, "poster_path": poster,
                    "tmdb_id": tmdb_id, "can_request": match.get('can_request', False), 
                    "overseerr_status": match.get('status')
                })
            full_report.append({"name": user['username'], "items": items_with_status})

        CACHE["plex_watchlists"] = full_report
        CACHE["last_update"] = datetime.now().strftime("%H:%M:%S")
        logger.info(f"✅ Scan terminé. {total_items} médias analysés.")
    except Exception as e:
        logger.error(f"❌ Erreur pendant run_sync: {e}")
    finally:
        IS_SCANNING = False
    
def get_version():
    try:
        # Si tu as copié le config.yaml dans le conteneur via le Dockerfile
        with open("/app/config.yaml", 'r') as f:
            for line in f:
                if line.startswith("version:"):
                    return line.split(":")[1].strip().replace('"', '').replace("'", "")
    except:
        pass
    return "0.3.5" # Fallback

VERSION = get_version()

# --- ROUTES FASTAPI ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    Thread(target=run_sync_loop, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="/app"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    opts = get_hass_options()
    all_items = []
    for wl in CACHE.get("plex_watchlists", []):
        for item in wl.get("items", []):
            item_copy = item.copy()
            item_copy["requested_by"] = wl["name"]
            all_items.append(item_copy)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "version": VERSION,
        "items_to_request": all_items,
        "logs": list(LOG_HISTORY),
        "cycle": CYCLE_COUNT,
        "dry_run": opts.get("dry_run", True),
        "is_scanning": IS_SCANNING,
        "stats": {"to_overseerr": len(all_items)},
        "api_status": CACHE["api_status"]
    })

@app.get("/sync")
async def force_sync():
    if not IS_SCANNING:
        Thread(target=run_sync, kwargs={"sync_users": True}).start()
        return {"status": "started"}
    return {"status": "already_running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1604)