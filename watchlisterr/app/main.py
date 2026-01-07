import sys
import logging
import json
import os
import time
from threading import Thread
from fastapi import FastAPI
import uvicorn
from overseerr_api import OverseerrClient
from plex_api import PlexClient

# 1. Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
sys.stdout.reconfigure(line_buffering=True)
logger = logging.getLogger("watchlisterr")

# 2. Variables de Cache
CACHE = {"status": "Initialisation...", "last_update": None, "stats": {}, "plex_watchlists": []}
IS_SCANNING = False

app = FastAPI()

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f:
            return json.load(f)
    return {}

def run_sync():
    """Logique de scan déplacée dans une fonction pour le cache"""
    global CACHE, IS_SCANNING
    if IS_SCANNING:
        return
    
    IS_SCANNING = True
    try:
        logger.info("Début du scan en arrière-plan...")
        options = get_hass_options()
        ov_client = OverseerrClient(options.get('overseerr_url'), options.get('overseerr_api_key'))
        plex_client = PlexClient(options.get('plex_token'))
        
        my_profile = plex_client.get_my_profile()
        friends = plex_client.get_friends() or []
        
        full_report = []
        stats = {"total_plex": 0, "already_on_plex": 0, "to_overseerr": 0}
        
        users_to_process = []
        if my_profile:
            users_to_process.append({"plex_id": None, "username": my_profile['username'], "role": "Admin"})
        for f in friends:
            users_to_process.append({"plex_id": f['plex_id'], "username": f['username'], "role": "Friend"})

        for user in users_to_process:
            watchlist = plex_client.get_watchlist(user['plex_id'])
            items_with_status = []
            user_total = len(watchlist)
            stats["total_plex"] += user_total
            
            for item in watchlist:
                match = ov_client.search_content(item['title'], item['year'], item['type'])
                if match['status'] == "Déjà présent sur Plex":
                    stats["already_on_plex"] += 1
                elif match.get('can_request'):
                    stats["to_overseerr"] += 1

                items_with_status.append({
                    "title": item['title'],
                    "year": item['year'],
                    "type": item['type'],
                    "overseerr_status": match['status'],
                    "tmdb_id": match['tmdb_id'],
                    "can_request": match.get('can_request', False)
                })
            
            full_report.append({
                "name": user['username'],
                "type": user['role'],
                "watchlist_count": user_total,
                "items": items_with_status
            })

        CACHE = {
            "status": "Données à jour",
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stats": stats,
            "plex_watchlists": full_report
        }
        logger.info(f"--- RÉSUMÉ : {stats['total_plex']} items trouvés | {stats['already_on_plex']} sur Plex | {stats['to_overseerr']} à commander ---")
    
    except Exception as e:
        logger.error(f"Erreur pendant le scan : {e}")
        CACHE["status"] = f"Erreur : {str(e)}"
    finally:
        IS_SCANNING = False

@app.on_event("startup")
def startup_event():
    # Lancement d'un scan immédiat au démarrage dans un thread séparé
    Thread(target=run_sync).start()

@app.get("/")
def read_root():
    """Renvoie instantanément le dernier cache"""
    return {
        "scan_in_progress": IS_SCANNING,
        "results": CACHE
    }

@app.get("/sync")
def force_sync():
    """Permet de forcer un scan manuellement"""
    if not IS_SCANNING:
        Thread(target=run_sync).start()
        return {"message": "Scan lancé"}
    return {"message": "Un scan est déjà en cours"}

@app.get("/check-overseerr")
def check_overseerr():
    options = get_hass_options()
    client = OverseerrClient(options.get('overseerr_url'), options.get('overseerr_api_key'))
    return client.get_status()

@app.get("/overseerr-users")
def get_overseerr_users():
    options = get_hass_options()
    client = OverseerrClient(options.get('overseerr_url'), options.get('overseerr_api_key'))
    return {"users": client.get_users()}

# Lancement
if __name__ == "__main__":
    logger.info("Démarrage de Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=1604)