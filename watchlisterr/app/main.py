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

@app.get("/")
def read_root():
    try:
        options = get_hass_options()
        
        # --- Overseerr ---
        ov_client = OverseerrClient(options.get('overseerr_url'), options.get('overseerr_api_key'))
        ov_status = ov_client.get_status()
        ov_users = ov_client.get_users() if ov_status.get("connected") else []

        # --- Plex ---
        plex_token = options.get('plex_token')
        plex_all_identities = []
        plex_connected = False
        test_watchlist = []
        
        if plex_token:
            plex_client = PlexClient(plex_token)
            
            # 1. Ton Profil
            my_profile = plex_client.get_my_profile()
            if my_profile:
                plex_all_identities.append(my_profile)
                plex_connected = True
                logger.info(f"Profil admin trouvé : {my_profile['username']} ({my_profile['plex_id']})")
                
                # TEST : On récupère TA propre watchlist
                test_watchlist = plex_client.get_watchlist(my_profile['plex_id'])
            
            # 2. Tes Amis
            friends_data = plex_client.get_friends()
            if friends_data:
                plex_all_identities.extend(friends_data)

        # --- Matching ---
        matching_table = []
        for ov_user in ov_users:
            match = next((p for p in plex_all_identities if str(p['username']).lower() == str(ov_user['name']).lower()), None)
            matching_table.append({
                "name": ov_user['name'],
                "overseerr_id": ov_user['id'],
                "plex_uuid": match['plex_id'] if match else "NON TROUVÉ",
                "status": "Match OK" if match else "Non trouvé sur Plex"
            })

        return {
            "status": "Watchlisterr is running",
            "connections": {"overseerr": ov_status.get("connected"), "plex": plex_connected},
            "my_watchlist_preview": test_watchlist[:5], # On affiche les 5 premiers pour tester
            "sync_mapping": matching_table
        }

    except Exception as e:
        logger.error(f"Erreur Ingress : {e}")
        return {"error": str(e)}

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