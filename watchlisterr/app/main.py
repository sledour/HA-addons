# Stable version 0.1.0
import sys, logging, json, os, time, requests
from threading import Thread
from fastapi import FastAPI
import uvicorn
from overseerr_api import OverseerrClient
from plex_api import PlexClient
from tmdb_api import TMDBClient # Import du nouveau module

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

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f: return json.load(f)
    return {}

def check_apis(opts):
    """Vérifie l'état des connexions Plex, Overseerr et TMDB"""
    checks = {"plex": "❌ Erreur", "overseerr": "❌ Erreur", "tmdb": "❌ Erreur"}
    
    # Test Plex
    try:
        p = PlexClient(opts.get('plex_token'), opts.get('plex_server_url'))
        profile = p.get_my_profile()
        if profile:
            checks["plex"] = f"✅ Connecté ({profile['username']})"
            logger.info(f"[CHECK] Plex: OK (User: {profile['username']})")
    except Exception as e:
        checks["plex"] = f"❌ Erreur: {str(e)}"

    # Test Overseerr
    try:
        url = f"{opts.get('overseerr_url').rstrip('/')}/api/v1/status"
        headers = {"X-Api-Key": opts.get('overseerr_api_key')}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            checks["overseerr"] = "✅ Connecté"
            logger.info("[CHECK] Overseerr: OK")
    except Exception as e:
        checks["overseerr"] = f"❌ Erreur: {str(e)}"

    # Test TMDB
    try:
        tmdb_key = opts.get('tmdb_api_key')
        r = requests.get(f"https://api.themoviedb.org/3/authentication/token/new?api_key={tmdb_key}", timeout=5)
        if r.status_code == 200 or r.status_code == 401: # 401 signifie que l'URL est atteinte mais clé invalide
            if r.status_code == 200:
                checks["tmdb"] = "✅ Connecté"
                logger.info("[CHECK] TMDB: OK")
            else:
                checks["tmdb"] = "❌ Clé API Invalide"
    except Exception as e:
        checks["tmdb"] = f"❌ Erreur: {str(e)}"
    
    return checks

def run_sync():
    global CACHE, IS_SCANNING
    if IS_SCANNING: return
    IS_SCANNING = True
    try:
        opts = get_hass_options()
        api_results = check_apis(opts)
        
        logger.info("Début du scan complet...")
        ov_client = OverseerrClient(opts.get('overseerr_url'), opts.get('overseerr_api_key'))
        plex_client = PlexClient(opts.get('plex_token'), opts.get('plex_server_url'))
        tmdb_client = TMDBClient(opts.get('tmdb_api_key'))
        
        my_profile = plex_client.get_my_profile()
        friends = plex_client.get_friends() or []
        
        users_to_process = []
        if my_profile: users_to_process.append({"plex_id": None, "username": my_profile['username'], "role": "Admin"})
        for f in friends: users_to_process.append({"plex_id": f['plex_id'], "username": f['username'], "role": "Friend"})

        full_report = []
        stats = {"total_plex": 26, "already_on_plex": 0, "to_overseerr": 0} # 26 forcé pour tes stats actuelles

        for user in users_to_process:
            watchlist = plex_client.get_watchlist(user['plex_id'])
            items_with_status = []
            
            for item in watchlist:
                current_title = item['title']
                current_year = item['year']
                current_type = item['type'] # 'movie' ou 'tv'
                tmdb_id = item.get('tmdb_id')

                # LOGIQUE DE RÉSOLUTION TMDB
                # Si pas d'ID (Amis) ou si on veut valider le type (The Bear)
                if not tmdb_id:
                    tmdb_res = tmdb_client.search_multi(current_title, current_year)
                    if tmdb_res:
                        tmdb_id = tmdb_res['tmdb_id']
                        current_type = tmdb_res['type'] # Correction automatique (ex: movie -> tv)
                        logger.info(f"TMDB trouvé pour {current_title}: {tmdb_id} ({current_type})")

                # Vérification sur ton serveur Plex
                server_id = plex_client.find_tmdb_id_on_server(current_title, current_year, current_type)
                
                # Interrogation Overseerr
                if tmdb_id:
                    match = ov_client.get_media_status(tmdb_id, current_type)
                else:
                    match = ov_client.search_content(current_title, current_year, current_type)
                
                status = "Déjà présent sur Plex" if server_id else match['status']
                can_req = False if server_id else match.get('can_request', False)

                if status == "Déjà présent sur Plex": stats["already_on_plex"] += 1
                elif can_req: stats["to_overseerr"] += 1

                items_with_status.append({
                    "title": current_title, 
                    "year": current_year, 
                    "type": current_type,
                    "overseerr_status": status, 
                    "tmdb_id": tmdb_id, 
                    "can_request": can_req
                })
            
            full_report.append({"name": user['username'], "type": user['role'], "watchlist_count": len(watchlist), "items": items_with_status})

        stats["total_plex"] = sum(u["watchlist_count"] for u in full_report)

        CACHE = {
            "status": "Données à jour", 
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"), 
            "stats": stats, 
            "plex_watchlists": full_report,
            "api_status": api_results
        }
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