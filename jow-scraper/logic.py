import asyncio
import re
from playwright.async_api import async_playwright

def parse_ingredient_line(text):
    """ Transforme '280 g Riz' en objet structuré pour Mealie """
    match = re.match(r"(\d+(?:[\.,]\d+)?)\s*([a-zA-Z\.]+)?\s*(.*)", text)
    if match:
        return {
            "note": text,
            "quantity": float(match.group(1).replace(',', '.')),
            "unit": {"name": match.group(2).strip() if match.group(2) else None},
            "food": {"name": match.group(3).strip()},
            "disableAmount": False
        }
    return {"note": text, "disableAmount": True}

async def get_recipe_links(share_url, page):
    """ Extrait tous les liens de recettes depuis une URL de partage Jow """
    await page.goto(share_url, wait_until="networkidle", timeout=30000)
    # Clic cookies rapide
    try:
        btn = page.locator("button:has-text('Accepter'), button:has-text('Tout accepter')")
        if await btn.is_visible(timeout=2000): await btn.click()
    except: pass
    
    await page.wait_for_selector('a[href*="/recipes/"]', timeout=10000)
    links = await page.locator('a[href*="/recipes/"]').all()
    
    urls = []
    for link in links:
        href = await link.get_attribute("href")
        if href:
            slug = href.split('/')[-1].split('?')[0]
            full_url = f"https://jow.fr/recipes/{slug}?coversCount=4"
            if full_url not in urls: urls.append(full_url)
    return urls

async def get_recipe_details(recipe_url, page):
    """ Extrait les ingrédients (pour 4) et les infos de base """
    await page.goto(recipe_url, wait_until="networkidle", timeout=30000)
    await page.wait_for_selector('h1', timeout=10000)
    
    # On laisse un peu de temps pour que le JS calcule les doses
    await asyncio.sleep(2)

    name = await page.locator('h1').inner_text()
    
    # --- STRATÉGIE A : Extraction visuelle (pour les doses exactes pour 4) ---
    ingredients = []
    # On teste plusieurs sélecteurs possibles pour Jow
    selectors = ['[class*="Ingredient__Container"]', '[class*="ingredient"]', 'li div[class*="Container"]']
    
    for selector in selectors:
        els = await page.query_selector_all(selector)
        if els:
            for el in els:
                txt = await el.inner_text()
                if txt and len(txt) > 2:
                    clean_txt = " ".join(txt.split())
                    # Éviter les doublons
                    parsed = parse_ingredient_line(clean_txt)
                    if not any(i.get('note') == parsed['note'] for i in ingredients):
                        ingredients.append(parsed)
            if ingredients: break

    # --- STRATÉGIE B : Secours JSON-LD (si A a échoué) ---
    if not ingredients:
        raw_ld = await page.evaluate('''() => {
            const script = Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                .find(s => s.innerText.includes('"@type":"Recipe"'));
            return script ? JSON.parse(script.innerText) : null;
        }''')
        if raw_ld and "recipeIngredient" in raw_ld:
            ingredients = [parse_ingredient_line(i) for i in raw_ld["recipeIngredient"]]

    return {
        "name": name.strip(),
        "recipeServings": 4,
        "recipeIngredient": ingredients,
        "orgURL": recipe_url
    }