import json
import os
from fastapi import FastAPI
from overseerr_api import OverseerrClient
import uvicorn

app = FastAPI()

def get_hass_options():
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, 'r') as f:
            return json.load(f)
    # Pour le test local en dehors de HASS, on peut mettre des valeurs par défaut
    return {
        "overseerr_url": "http://192.168.1.50:5055",
        "overseerr_api_key": "TON_API_KEY"
    }

@app.get("/")
def read_root():
    return {"status": "Watchlisterr is running", "ingress_port": 1604}

@app.get("/test-overseerr")
def test_overseerr():
    options = get_hass_options()
    client = OverseerrClient(options['overseerr_url'], options['overseerr_api_key'])
    
    connected = client.test_connection()
    if not connected:
        return {"error": "Impossible de se connecter à Overseerr. Vérifiez l'URL et la clé API."}
    
    users = client.get_users_mapping()
    return {
        "connected": True,
        "user_count": len(users) if users else 0,
        "users": users
    }

if __name__ == "__main__":
    # On écoute sur 0.0.0.0 pour que Ingress puisse y accéder
    uvicorn.run(app, host="0.0.0.0", port=1604)