import requests
import json

# L'URL de ton partage Jow (celle avec la clé)
SHARE_URL = "https://jow.fr/cooking/recipes-selection/db538f22-1c85-4bfb-9134-888482ee6149?key=3fd819f62aa3810dcda3668a29702d2d5ff14c977572c050ad9c36101bf1163e&action=menuSharing&firstName=S%C3%A9bastien&didRedirect=undefined&userId=5d3746b8cda8245c8c8339ef"

def test():
    print("1. Test de récupération des liens...")
    r_links = requests.post("http://localhost:5000/get-links", json={"url": SHARE_URL})
    urls = r_links.json().get("urls", [])
    print(f"✅ {len(urls)} recettes trouvées.")

    if urls:
        print(f"2. Test d'extraction sur la première recette : {urls[0]}")
        r_details = requests.post("http://localhost:5000/get-details", json={"url": urls[0]})
        print("\n--- DONNÉES REÇUES (À ENVOYER EN PUT À MEALIE) ---")
        print(json.dumps(r_details.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test()