import sys
import logging
import json
import os
from fastapi import FastAPI
import uvicorn
from overseerr_api import OverseerrClient
from plex_api import PlexClient
from fastapi.responses import HTMLResponse

# 1. Configuration des logs pour HASS
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
sys.stdout.reconfigure(line_buffering=True)

logger = logging.getLogger("watchlisterr")

print("-------------------------------------------------------")
print("   WATCHLISTERR - SERVEUR ACTIF (PORT 1604)            ")
print("-------------------------------------------------------")

app = FastAPI()

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f:
            return json.load(f)
    return {}

@app.on_event("startup")
def startup_event():
    logger.info("Vérification des connexions au démarrage...")
    options = get_hass_options()
    
    # Check Overseerr
    ov_url = options.get('overseerr_url')
    ov_key = options.get('overseerr_api_key')
    if ov_url and ov_key:
        ov_client = OverseerrClient(ov_url, ov_key)
        ov_res = ov_client.get_status()
        if ov_res["connected"]:
            logger.info(f"VÉRIFICATION : Connecté à Overseerr (v{ov_res['details'].get('version')})")
        else:
            logger.error(f"VÉRIFICATION : Échec Overseerr : {ov_res.get('error')}")

    # Check Plex
    plex_token = options.get('plex_token')
    if plex_token:
        plex_client = PlexClient(plex_token)
        friends = plex_client.get_friends()
        if friends is not None:
            logger.info(f"VÉRIFICATION : Connecté à Plex (Amis trouvés: {len(friends)})")
        else:
            logger.error("VÉRIFICATION : Échec connexion Plex (Vérifiez le Token)")
    else:
        logger.warning("VÉRIFICATION : Token Plex manquant")

@app.get("/")
def read_root():
    try:
        options = get_hass_options()
        ov_client = OverseerrClient(options.get('overseerr_url'), options.get('overseerr_api_key'))
        plex_client = PlexClient(options.get('plex_token'))
        
        my_profile = plex_client.get_my_profile()
        friends = plex_client.get_friends() or []
        
        full_report = []
        stats = {
            "total_plex": 0,
            "already_on_plex": 0,
            "to_overseerr": 0
        }
        
        # Liste de tous les comptes à traiter
        users_to_process = []
        if my_profile:
            users_to_process.append({"plex_id": None, "username": my_profile['username'], "role": "Admin"})
        
        for f in friends:
            users_to_process.append({"plex_id": f['plex_id'], "username": f['username'], "role": "Friend"})

        # Traitement de chaque utilisateur
        for user in users_to_process:
            watchlist = plex_client.get_watchlist(user['plex_id'])
            items_with_status = []
            
            user_total = len(watchlist)
            stats["total_plex"] += user_total
            
            for item in watchlist:
                # Match avec Overseerr
                match = ov_client.search_content(item['title'], item['year'], item['type'])
                
                # Mise à jour des compteurs globaux
                if match['status'] == "Déjà présent sur Plex":
                    stats["already_on_plex"] += 1
                elif match['can_request']:
                    stats["to_overseerr"] += 1

                items_with_status.append({
                    "title": item['title'],
                    "year": item['year'],
                    "type": item['type'],
                    "overseerr_status": match['status'],
                    "tmdb_id": match['tmdb_id'],
                    "can_request": match['can_request']
                })

            logger.info(f"SYNCHRO : {user['username']} ({user['role']}) - {user_total} items analysés")
            
            full_report.append({
                "name": user['username'],
                "type": user['role'],
                "watchlist_count": user_total,
                "items": items_with_status
            })

        # Log final détaillé
        logger.info(f"--- RÉSUMÉ : {stats['total_plex']} items trouvés | {stats['already_on_plex']} déjà sur Plex | {stats['to_overseerr']} à envoyer vers Overseerr ---")

        return {
            "status": "Watchlisterr - Analysis Complete",
            "stats": stats,
            "plex_watchlists": full_report
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données : {e}")
        return {"error": str(e)}

@app.get("/check-overseerr")
def check_overseerr():
    options = get_hass_options()
    url = options.get('overseerr_url')
    api_key = options.get('overseerr_api_key')
    
    if not url or not api_key:
        return {"connected": False, "error": "URL ou Clé API manquante"}
    
    client = OverseerrClient(url, api_key)
    result = client.get_status()
    return result

@app.get("/overseerr-users")
def get_overseerr_users():
    options = get_hass_options()
    client = OverseerrClient(options.get('overseerr_url'), options.get('overseerr_api_key'))
    users = client.get_users()
    return {"count": len(users), "users": users}

# Lancement
logger.info("Démarrage de Uvicorn...")
uvicorn.run(app, host="0.0.0.0", port=1604, log_level="info")