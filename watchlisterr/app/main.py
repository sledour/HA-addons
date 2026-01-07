import sys
import logging
import json
import os
from fastapi import FastAPI
import uvicorn
from overseerr_api import OverseerrClient
from plex_api import PlexClient

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
    logger.info("Vérification de la connexion Overseerr au démarrage...")
    options = get_hass_options()
    url = options.get('overseerr_url')
    api_key = options.get('overseerr_api_key')
    
    if url and api_key:
        client = OverseerrClient(url, api_key)
        result = client.get_status()
        if result["connected"]:
            logger.info(f"VÉRIFICATION : Connecté à Overseerr (v{result['details'].get('version')})")
        else:
            logger.error(f"VÉRIFICATION : Échec connexion Overseerr : {result.get('error')}")
    else:
        logger.warning("VÉRIFICATION : Paramètres Overseerr manquants dans la config HASS")

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f:
            return json.load(f)
    return {}

@app.get("/")
def read_root():
    options = get_hass_options()
    
    # --- Overseerr Part ---
    ov_url = options.get('overseerr_url')
    ov_key = options.get('overseerr_api_key')
    ov_client = OverseerrClient(ov_url, ov_key)
    ov_status = ov_client.get_status()
    ov_users = ov_client.get_users() if ov_status["connected"] else []

    # --- Plex Part ---
    plex_token = options.get('plex_token')
    plex_friends = []
    plex_connected = False
    
    if plex_token:
        plex_client = PlexClient(plex_token)
        friends_data = plex_client.get_friends()
        if friends_data is not None:
            plex_connected = True
            plex_friends = friends_data

    # --- Combined Response ---
    return {
        "status": "Watchlisterr is running",
        "overseerr": {
            "connected": ov_status["connected"],
            "version": ov_status.get("details", {}).get("version", "N/A"),
            "users_count": len(ov_users),
            "users": ov_users
        },
        "plex": {
            "connected": plex_connected,
            "friends_count": len(plex_friends),
            "friends": plex_friends
        }
    }

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