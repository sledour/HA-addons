# 0.3.5 - UI Dashboard Full Sync + Fix Posters & Names + Detailed Logs
import sys, logging, json, os, time, requests, sqlite3, collections
from threading import Thread
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response  # <--- AJOUT : Response
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
        
        # --- 1. MAPPING UTILISATEURS ---
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
       
        # --- 2. EXTRACTION DES MÉDIAS UNIQUES ---
        # On regroupe par titre+année pour ne pas appeler TMDB 10 fois pour le même film
        unique_items = {}
        user_watchlists = {} # Pour reconstruire le rapport final

        for user in users_to_process:
            watchlist = plex_client.get_watchlist(user['plex_id'])
            logger.info(f"👤 Traitement de : {user['username']} ({len(watchlist)} médias)")
            user_watchlists[user['username']] = watchlist
            for item in watchlist:
                key = f"{item['title']}-{item['year']}".lower()
                if key not in unique_items:
                    unique_items[key] = item

        # --- 3. TRAITEMENT DES MÉDIAS (CACHE OU TMDB) ---
        media_info_map = {} # Stocke les résultats (tmdb_id, poster, etc.)
        
        for key, item in unique_items.items():
            cached = db.get_cached_media(item['title'], item['year'])
            
            if cached and cached.get('poster_path') and cached['poster_path'] != "None":
                logger.info(f"📦 DEBUG DB | {item['title']} chargé depuis cache")
                media_info_map[key] = {
                    "tmdb_id": cached['tmdb_id'],
                    "m_type": cached['media_type'],
                    "poster": cached['poster_path']
                }
            else:
                # 1. On détermine le type correct pour TMDB
                # Plex peut renvoyer 'show', 'season', 'episode' ou 'movie'
                plex_type = item.get('type', 'movie')
                if plex_type in ['show', 'tv', 'season', 'episode']:
                    search_type = 'tv'
                else:
                    search_type = 'movie'

                logger.info(f"🔎 Recherche TMDB ({search_type}) pour : {item['title']}")
                
                tmdb_res = tmdb_client.search_multi(
                    title=item['title'], 
                    year=item['year'],
                    target_id=item.get('tmdb_id'),
                    media_type=search_type  # <--- On utilise search_type ici
                )
                
                if tmdb_res:
                    db.save_media(tmdb_res['tmdb_id'], item['title'], tmdb_res['type'], item['year'], tmdb_res['poster_path'])
                    logger.info(f"✅ Mis en cache : {item['title']}")
                    media_info_map[key] = {
                        "tmdb_id": tmdb_res['tmdb_id'],
                        "m_type": tmdb_res['type'],
                        "poster": tmdb_res['poster_path']
                    }
                else:
                    media_info_map[key] = {"tmdb_id": None, "m_type": item['type'], "poster": None}

        # --- 4. RÉGÉNÉRATION DU RAPPORT CACHÉ ---
        full_report = []
        for username, watchlist in user_watchlists.items():
            items_with_status = []
            for item in watchlist:
                key = f"{item['title']}-{item['year']}".lower()
                info = media_info_map.get(key, {})
                
                # Check Overseerr Status
                tmdb_id = info.get('tmdb_id')
                m_type = info.get('m_type', item['type'])
                match = ov_client.get_media_status(tmdb_id, m_type) if tmdb_id else {'status': 'Inconnu', 'can_request': False}
                on_server = plex_client.find_tmdb_id_on_server(item['title'], item['year'], m_type) is not None
                
                items_with_status.append({
                    "title": item['title'], 
                    "type": m_type, 
                    "poster_path": info.get('poster'),
                    "tmdb_id": tmdb_id, 
                    "can_request": match.get('can_request', False), 
                    "overseerr_status": match.get('status'),
                    "overseerr_id": True if match.get('status') in ['PENDING', 'PROCESSING', 'PARTIALLY_AVAILABLE'] else False, # ID pour icône Overseerr
                    "on_server": on_server, # Flag pour icône Plex
                    "requested_by": username # Optionnel pour affichage
                })
            full_report.append({"name": username, "items": items_with_status})

        CACHE["plex_watchlists"] = full_report
        CACHE["last_update"] = datetime.now().strftime("%H:%M:%S")
        logger.info(f"✅ Scan terminé. {len(unique_items)} médias uniques traités.")

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
            # ON S'ASSURE QUE LE POSTER EST COPIÉ ICI
            item_copy["poster_path"] = item.get("poster_path")
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

# ROUTE PROXY POUR LES IMAGES (FIX HA INGRESS)
@app.get("/proxy-image")
async def proxy_image(url: str = None):
    if not url or url == "None":
        return Response(status_code=400)
    try:
        # On force un timeout court pour ne pas bloquer l'UI
        r = requests.get(url, headers={"User-Agent": "Watchlisterr/1.0"}, timeout=5)
        return Response(content=r.content, media_type="image/jpeg")
    except Exception as e:
        logger.error(f"❌ Erreur Proxy: {e}")
        return Response(status_code=404)

@app.get("/debug-db")
async def debug_db(request: Request):
    users = db.get_all_users()  # Assure-toi que cette méthode existe dans database.py
    media = db.get_all_media()  # Idem
    return templates.TemplateResponse("debug.html", {
        "request": request,
        "users": users,
        "media": media
    })

@app.post("/clear-db")
async def clear_db():
    try:
        db.clear_tables()
        logger.warning("🧹 Base de données vidée par l'utilisateur")
        return {"status": "success", "message": "Base de données vidée."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1604)