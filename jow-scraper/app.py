from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright
from logic import get_recipe_links, get_recipe_details

app = Flask(__name__)

# Fonction utilitaire pour isoler la gestion de Playwright
async def run_in_browser(func, url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # On définit un User-Agent pour éviter d'être bloqué
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            res = await func(url, page)
            return res
        finally:
            await browser.close()

@app.route('/get-links', methods=['POST'])
async def links():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL manquante"}), 400
    
    try:
        res = await run_in_browser(get_recipe_links, url)
        return jsonify({"urls": res})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-details', methods=['POST'])
async def details():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL manquante"}), 400

    try:
        res = await run_in_browser(get_recipe_details, url)
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Important pour Playwright : s'assurer que Flask ne tourne pas en mode multi-threadé complexe ici
    app.run(host='0.0.0.0', port=5000, debug=False)