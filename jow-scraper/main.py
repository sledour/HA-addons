from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

async def run_scraper(share_url):
    results = []
    async with async_playwright() as p:
        # headless=True est obligatoire sur un serveur sans écran
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto(share_url, wait_until="domcontentloaded", timeout=30000)
            
            # Clic cookies rapide
            try:
                btn = page.locator("button:has-text('Accepter'), button:has-text('Tout accepter')")
                if await btn.is_visible(timeout=3000):
                    await btn.click()
            except: pass

            # Attente d'un élément de recette (plus générique que ton prénom pour que ça marche pour d'autres)
            await page.wait_for_selector('a[href*="/recipes/"]', timeout=15000)
            
            recipe_links = page.locator('a[href*="/recipes/"]')
            count = await recipe_links.count()
            
            for i in range(count):
                link_el = recipe_links.nth(i)
                href = await link_el.get_attribute("href")
                name = await link_el.inner_text()
                name = name.split('\n')[0].strip()
                
                if href and "/recipes/" in href:
                    slug = href.split('/')[-1].split('?')[0]
                    if not any(r['slug'] == slug for r in results):
                        results.append({
                            "slug": slug,
                            "name": name or slug,
                            "url": f"https://jow.fr/recipes/{slug}?coversCount=4"
                        })
        finally:
            await browser.close()
    return results

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL manquante"}), 400
    
    # Exécution de l'async dans Flask
    recipes = asyncio.run(run_scraper(url))
    return jsonify(recipes)

if __name__ == '__main__':
    # Écoute sur toutes les interfaces pour Docker
    app.run(host='0.0.0.0', port=5000)