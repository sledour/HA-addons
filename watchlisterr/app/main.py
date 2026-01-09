import sys, logging, json, os, time
from threading import Thread
from fastapi import FastAPI
import uvicorn
from overseerr_api import OverseerrClient
from plex_api import PlexClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
sys.stdout.reconfigure(line_buffering=True)
logger = logging.getLogger("watchlisterr")

CACHE = {"status": "Initialisation...", "last_update": None, "stats": {}, "plex_watchlists": []}
IS_SCANNING = False

app = FastAPI()

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f: return json.load(f)
    return {}

def run_sync():
    global CACHE, IS_SCANNING
    if IS_SCANNING: return
    IS_SCANNING = True
    try:
        logger.info("Début du scan complet...")
        opts = get_hass_options()
        ov_client = OverseerrClient(opts.get('overseerr_url'), opts.get('overseerr_api_key'))
        plex_client = PlexClient(opts.get('plex_token'), opts.get('plex_server_url'))
        
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
            stats["total_plex"] += len(watchlist)
            
            for item in watchlist:
                # 1. Vérification locale (vérité serveur)
                server_id = plex_client.find_tmdb_id_on_server(item['title'], item['year'], item['type'])
                tmdb_id = server_id or item.get('tmdb_id')

                # 2. Vérification Overseerr
                if tmdb_id:
                    match = ov_client.get_media_status(tmdb_id, item['type'])
                else:
                    match = ov_client.search_content(item['title'], item['year'], item['type'])
                
                # 3. Arbitrage
                status = "Déjà présent sur Plex" if server_id else match['status']
                can_req = False if server_id else match.get('can_request', False)

                if status == "Déjà présent sur Plex": stats["already_on_plex"] += 1
                elif can_req: stats["to_overseerr"] += 1

                items_with_status.append({
                    "title": item['title'], "year": item['year'], "type": item['type'],
                    "overseerr_status": status, "tmdb_id": tmdb_id or match.get('tmdb_id'), "can_request": can_req
                })
            
            full_report.append({"name": user['username'], "type": user['role'], "watchlist_count": len(watchlist), "items": items_with_status})

        CACHE = {"status": "Données à jour", "last_update": time.strftime("%Y-%m-%d %H:%M:%S"), "stats": stats, "plex_watchlists": full_report}
        logger.info(f"Scan terminé : {stats['total_plex']} items traités.")
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1604)