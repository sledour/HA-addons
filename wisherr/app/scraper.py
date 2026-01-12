import requests
from bs4 import BeautifulSoup
import json

def scrape_amazon(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.amazon.fr/",
        "DNT": "1"
    }
    
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code != 200:
            print(f"Erreur Amazon : Code {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 1. TITRE
        title_tag = soup.find("span", {"id": "productTitle"})
        title = title_tag.get_text().strip() if title_tag else "Produit Amazon"

        # 2. PRIX (Nettoyage renforcé)
        price = "?? €"
        # On cherche la balise 'a-offscreen' qui contient souvent le prix propre pour les lecteurs d'écran
        price_tag = soup.select_one("span.a-price span.a-offscreen") or soup.find("span", {"id": "priceblock_ourprice"})
        
        if price_tag:
            price = price_tag.get_text().strip()
        else:
            # Backup : construction manuelle si offscreen absent
            whole = soup.find("span", {"class": "a-price-whole"})
            fraction = soup.find("span", {"class": "a-price-fraction"})
            if whole:
                # On enlève les points de séparation des milliers et on nettoie
                price_text = "".join(filter(str.isdigit, whole.get_text()))
                price_frac = fraction.get_text().strip() if fraction else "00"
                price = f"{price_text},{price_frac}€"

        # 3. IMAGE (Récupération de la version HD)
        image_url = None
        img_tag = soup.find("img", {"id": "landingImage"})
        if img_tag:
            # Amazon stocke un dictionnaire JSON de tailles dans 'data-a-dynamic-image'
            # On prend la clé (URL) qui a la plus grande valeur (résolution)
            dyn_img = img_tag.get("data-a-dynamic-image")
            if dyn_img:
                try:
                    images_dict = json.loads(dyn_img)
                    image_url = list(images_dict.keys())[-1] # La dernière est souvent la plus grande
                except:
                    image_url = img_tag.get("src")
            else:
                image_url = img_tag.get("src")

        return {
            "title": title[:100],
            "price": price,
            "image_url": image_url,
            "product_url": url
        }
    except Exception as e:
        print(f"Erreur Scraping détaillé : {e}")
        return None