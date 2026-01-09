# 0.3.5 - UI Dashboard + Matrix Logs + Poster Support
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
# Handler Console
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(sh)
# Handler UI
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
templates = Jinja2Templates(directory="templates")

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f: return json.load(f)
    return {}

# --- LOGIQUE DE SYNCHRONISATION ---

def run_sync_loop():
    """Boucle principale réactive"""
    global CYCLE_COUNT
    logger.info("🚀 Démarrage de la boucle réactive")
    
    while True:
        try:
            opts = get_hass_options()
            interval = opts.get("sync_interval", 3)
            is_dry_run = opts.get("dry_run", True)
            
            # 1. Sync Users tous les 100 cycles (ou au cycle 0)
            include_users = (CYCLE_COUNT % 100 == 0)
            
            # 2. Exécution du scan
            run_sync(sync_users=include_users)
            
            # Traitement des requêtes
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
                                title=item["title"],
                                is_simulation=is_dry_run
                            )

            CYCLE_COUNT += 1
            logger.info(f"💤 Cycle {CYCLE_COUNT} terminé. Attente {interval} min.")
            time.sleep(interval * 60)
            
        except Exception as e:
            logger.error(f"💥 Erreur boucle : {e}")
            time.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ce qui se passe au démarrage
    Thread(target=run_sync_loop, daemon=True).start()
    yield
    # Ce qui se passe à l'arrêt (si besoin)

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="./"), name="static")
db = Database()

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
                logger.info(f"✅ Mapping : {p_user['username']} -> Overseerr ID {match['id']}")
            else:
                logger.warning(f"⚠️ Aucun compte Overseerr pour {p_user['username']}")
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
            # Code de mapping users identique au tien...
            pass 

        logger.info("🔍 Scan des Watchlists en cours...")
        # Simulation d'acquisition des profils (ton code existant ici)
        users_to_process = [{"plex_id": None, "username": "Admin", "role": "Admin"}] # Simplifié pour l'exemple
        
        full_report = []
        for user in users_to_process:
            watchlist = plex_client.get_watchlist(user['plex_id'])
            items_with_status = []
            for item in watchlist:
                # Récupération TMDB + Poster
                cached = db.get_cached_media(item['title'], item['year'])
                if cached:
                    tmdb_id, m_type, poster = cached['tmdb_id'], cached['media_type'], cached.get('poster_path')
                else:
                    tmdb_res = tmdb_client.search_multi(item['title'], item['year'])
                    if tmdb_res:
                        tmdb_id, m_type, poster = tmdb_res['tmdb_id'], tmdb_res['type'], tmdb_res.get('poster_path')
                        db.save_media(tmdb_id, item['title'], m_type, item['year'], poster)
                
                # Status Overseerr
                match = ov_client.get_media_status(tmdb_id, m_type) if tmdb_id else {'status': 'Inconnu', 'can_request': False}
                
                items_with_status.append({
                    "title": item['title'], "type": m_type, "poster_path": poster,
                    "can_request": match.get('can_request', False), "requested_by": user['username']
                })
            full_report.append({"name": user['username'], "items": items_with_status})

        CACHE["plex_watchlists"] = full_report
        CACHE["last_update"] = datetime.now().strftime("%H:%M:%S")
        logger.info("✅ Scan terminé avec succès.")
    finally:
        IS_SCANNING = False

# --- ROUTES FASTAPI ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    Thread(target=run_sync_loop, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="./"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    opts = get_hass_options()
    
    # On aplatit les watchlists pour l'affichage de la Media Bar
    all_items = []
    for wl in CACHE.get("plex_watchlists", []):
        for item in wl.get("items", []):
            all_items.append(item)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "items_to_request": all_items,
        "logs": list(LOG_HISTORY),
        "cycle": CYCLE_COUNT,
        "dry_run": opts.get("dry_run", True),
        "is_scanning": IS_SCANNING,
        "stats": {"to_overseerr": len(all_items)}
    })

@app.get("/sync")
async def force_sync():
    if not IS_SCANNING:
        Thread(target=run_sync, kwargs={"sync_users": True}).start()
        return {"status": "started"}
    return {"status": "already_running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1604)