import sys
import logging
import json
import os
from fastapi import FastAPI
import uvicorn
from overseerr_api import OverseerrClient

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

@app.get("/")
def read_root():
    return {"status": "Watchlisterr is running"}

@app.get("/test-overseerr")
def test_overseerr():
    options = get_hass_options()
    client = OverseerrClient(options.get('overseerr_url', ''), options.get('overseerr_api_key', ''))
    
    connected = client.test_connection()
    if not connected:
        return {"error": "Connexion échouée à Overseerr"}
    
    users = client.get_users_mapping()
    return {"connected": True, "users": users}

# Lancement direct (sans condition) pour garantir que S6 voit le processus
logger.info("Démarrage de Uvicorn...")
uvicorn.run(app, host="0.0.0.0", port=1604, log_level="info")