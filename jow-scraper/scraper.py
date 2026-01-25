import json
import asyncio
from playwright.async_api import async_playwright

async def scrape_jow_visual(share_url):
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"🚀 Navigation vers : {share_url}")
        try:
            # 1. Chargement
            await page.goto(share_url, wait_until="domcontentloaded", timeout=40000)
            
            # 2. Cookies
            try:
                btn = page.locator("button:has-text('Accepter'), button:has-text('Tout accepter')")
                if await btn.is_visible(timeout=3000):
                    await btn.click()
            except: pass

            # 3. Attente de ta session
            await page.wait_for_selector("text=Sébastien", timeout=15000)
            
            # 4. Extraction des liens de recettes
            # Sur Jow, les recettes dans une sélection sont des liens <a> qui pointent vers /recipes/...
            print("🧐 Analyse des éléments visuels...")
            
            # On cherche tous les liens qui contiennent "/recipes/" dans leur href
            recipe_links = page.locator('a[href*="/recipes/"]')
            
            count = await recipe_links.count()
            for i in range(count):
                link_el = recipe_links.nth(i)
                href = await link_el.get_attribute("href")
                
                # On essaie de choper le titre (souvent dans un h3 ou un span à l'intérieur du lien)
                name = await link_el.inner_text()
                name = name.split('\n')[0].strip() # Nettoyage si plusieurs lignes
                
                if href and "/recipes/" in href:
                    # Nettoyage de l'URL pour avoir le format propre
                    slug = href.split('/')[-1].split('?')[0]
                    clean_url = f"https://jow.fr/recipes/{slug}?coversCount=4"
                    
                    if not any(r['slug'] == slug for r in results):
                        results.append({
                            "slug": slug,
                            "name": name or slug,
                            "url": clean_url
                        })

        except Exception as e:
            print(f"🔴 Erreur : {e}")
        finally:
            await browser.close()
    
    if not results:
        print("⚠️ Aucune recette trouvée visuellement.")
    else:
        print(f"\n✅ {len(results)} RECETTES TROUVÉES SUR LA PAGE :")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    return results

if __name__ == "__main__":
    URL_PARTAGE = "https://jow.fr/cooking/recipes-selection/db538f22-1c85-4bfb-9134-888482ee6149?key=3fd819f62aa3810dcda3668a29702d2d5ff14c977572c050ad9c36101bf1163e&action=menuSharing&firstName=S%C3%A9bastien&didRedirect=undefined&userId=5d3746b8cda8245c8c8339ef"
    asyncio.run(scrape_jow_visual(URL_PARTAGE))