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

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f:
            return json.load(f)
    return {}

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        options = get_hass_options()
        ov_client = OverseerrClient(options.get('overseerr_url'), options.get('overseerr_api_key'))
        plex_client = PlexClient(options.get('plex_token'))
        
        my_profile = plex_client.get_my_profile()
        friends = plex_client.get_friends() or []
        
        full_report = []
        global_count = 0  # Compteur global
        
        # 1. Traitement Admin
        if my_profile:
            my_watchlist = plex_client.get_watchlist()
            count = len(my_watchlist)
            global_count += count
            
            logger.info(f"SYNCHRO : {my_profile['username']} (Admin) - {count} items trouvés")
            
            full_report.append({
                "name": my_profile['username'],
                "type": "Admin",
                "watchlist_count": count,
                "items": my_watchlist
            })

        # 2. Traitement Amis
        for friend in friends:
            friend_watchlist = plex_client.get_watchlist(friend['plex_id'])
            count = len(friend_watchlist)
            global_count += count
            
            logger.info(f"SYNCHRO : {friend['username']} (Friend) - {count} items trouvés")
            
            full_report.append({
                "name": friend['username'],
                "type": "Friend",
                "watchlist_count": count,
                "items": friend_watchlist
            })

        # Log du total final
        logger.info(f"--- TOTAL : {global_count} éléments récupérés sur l'ensemble des Watchlists ---")

        return {
            "status": "Watchlisterr - Data Synced",
            "stats": {
                "total_items": global_count,
                "users_scanned": len(full_report)
            },
            "plex_watchlists": full_report
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données : {e}")
        return {"error": str(e)}
    
    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: sans-serif; background: #111; color: white; padding: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #333; padding: 10px; text-align: left; }}
                th {{ background: #222; }}
                .badge-movie {{ background: #007bff; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }}
                .badge-tv {{ background: #28a745; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <h1>Watchlisterr Dashboard</h1>
            <p>Total items: {global_count} across {len(full_report)} users.</p>
            </body>
    </html>
    """
    return html_content

@app.get("/check-overseerr")
def check_overseerr():
    options = get_hass_options()
    url = options.get('overseerr_url')
    api_key = options.get('overseerr_api_key')
    
    if not url or not api_key:
        return {
            "connected": False, 
            "error": "URL ou Clé API manquante dans la configuration de l'addon"
        }
    
    client = OverseerrClient(url, api_key)
    result = client.get_status()
    
    if result["connected"]:
        # On log le succès dans les logs de l'addon
        logger.info(f"Connexion réussie à Overseerr version: {result['details'].get('version')}")
    
    return result
@app.get("/overseerr-users")
def get_overseerr_users():
    options = get_hass_options()
    client = OverseerrClient(options.get('overseerr_url'), options.get('overseerr_api_key'))
    
    users = client.get_users()
    
    logger.info(f"Utilisateurs Overseerr trouvés : {len(users)}")
    return {
        "count": len(users),
        "users": users
    }

# Lancement direct (sans condition) pour garantir que S6 voit le processus
logger.info("Démarrage de Uvicorn...")
uvicorn.run(app, host="0.0.0.0", port=1604, log_level="info")