from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi import UploadFile, File
import shutil
import uuid
from fastapi import Response
from .scraper import scrape_amazon
import re

# Charge les variables du fichier .env dans l'environnement
load_dotenv()

from . import models, auth, database

# Création des tables au démarrage
models.Base.metadata.create_all(bind=database.engine)

# On récupère le chemin du dossier racine (wisherr/)
# __file__ est dans wisherr/app/, donc on remonte d'un cran
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# On s'assure que le dossier existe
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app = FastAPI(title="Wisherr")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory="app/templates")
SECRET_KEY = os.getenv("SECRET_KEY", "RE_nWt3GVROYbPGYCGiXMPmb4TqgoPyvfFajKMM96Mc")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Dépendance pour la DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_dashboard(request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user_from_cookie(request, db)
    if not user:
        # Si l'utilisateur n'existe plus en DB, on le renvoie au login
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Identifiants invalides"})
    
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    auth.create_session_cookie(response, user.username)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # 1. Vérifier si l'utilisateur existe déjà
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "error": "Ce nom d'utilisateur est déjà pris."
        })
    
    # 2. Créer le nouvel utilisateur
    new_user = models.User(
        username=username,
        hashed_password=auth.get_password_hash(password)
    )
    
    db.add(new_user)
    db.commit()
    
    # 3. Connecter automatiquement l'utilisateur après inscription
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    auth.create_session_cookie(response, new_user.username)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login?msg=logged_out", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("wisherr_session")
    return response

@app.post("/notes/add")
async def add_note(request: Request, content: str = Form(...), db: Session = Depends(get_db)):
    user = auth.get_current_user_from_cookie(request, db)
    if not user: return HTMLResponse(status_code=403)
    
    new_note = models.QuickNote(content=content, user_id=user.id)
    db.add(new_note)
    db.commit()
    
    # On renvoie juste le petit fragment HTML de la nouvelle note 
    # pour que HTMX l'insère dans la page
    return templates.TemplateResponse("fragments/note_item.html", {"request": request, "note": new_note})

@app.get("/notes/delete/{note_id}")
async def delete_note(note_id: int, request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user_from_cookie(request, db)
    note = db.query(models.QuickNote).filter(models.QuickNote.id == note_id, models.QuickNote.user_id == user.id).first()
    if note:
        db.delete(note)
        db.commit()
    return HTMLResponse("") # Renvoie vide pour que HTMX supprime l'élément

@app.post("/items/manual")
async def add_item_manual(
    request: Request,
    title: str = Form(...),
    price: str = Form(None),
    source_type: str = Form("manual"),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user = auth.get_current_user_from_cookie(request, db)
    if not user: return RedirectResponse(url="/login", status_code=303)

    # DETECTION DE LIEN AMAZON
    # On vérifie si le titre ressemble à une URL Amazon
    if ("amazon" in title.lower() or "amzn" in title.lower()) and title.startswith("http"):
        data = scrape_amazon(title)
        if data:
            # Si le scraping réussit, on enregistre les données
            new_item = models.Item(
                title=data["title"],
                price=data["price"],
                image_url=data["image_url"],
                product_url=data["product_url"],
                source_type="Amazon",
                user_id=user.id
            )
            db.add(new_item)
            db.commit()
            return RedirectResponse(url="/", status_code=303)
        else:
            # SI LE SCRAPING ÉCHOUE : On ne garde pas l'URL comme titre !
            # On met un titre par défaut pour ne pas casser le JavaScript
            title = "Lien Amazon (Echec Scraping)"

    # SINON : AJOUT MANUEL CLASSIQUE
    image_url = None
    if image and image.filename:
        file_name = f"{uuid.uuid4()}{os.path.splitext(image.filename)[1]}"
        file_path = os.path.join(STATIC_DIR, "uploads", file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/static/uploads/{file_name}"

    new_item = models.Item(
        title=title,
        price=price,
        image_url=image_url,
        source_type=source_type,
        user_id=user.id
    )
    db.add(new_item)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/items/update")
async def update_item(
    request: Request,
    item_id: int = Form(...),
    title: str = Form(...),
    price: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user = auth.get_current_user_from_cookie(request, db)
    item = db.query(models.Item).filter(models.Item.id == item_id, models.Item.user_id == user.id).first()
    
    if item:
        item.title = title
        item.price = price
        
        if image and image.filename:
            file_name = f"{uuid.uuid4()}{os.path.splitext(image.filename)[1]}"
            file_path = os.path.join(STATIC_DIR, "uploads", file_name)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            item.image_url = f"/static/uploads/{file_name}"
        
        db.commit()
    
    return RedirectResponse(url="/", status_code=303)

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    # 1. Vérifier si l'utilisateur est connecté
    user = auth.get_current_user_from_cookie(request, db)
    if not user:
        return Response(status_code=403)

    # 2. Chercher l'article appartenant à cet utilisateur
    item = db.query(models.Item).filter(
        models.Item.id == item_id, 
        models.Item.user_id == user.id
    ).first()

    if item:
        # 3. Supprimer le fichier image du disque s'il existe
        if item.image_url:
            # On transforme l'URL /static/uploads/... en chemin local
            relative_path = item.image_url.lstrip('/')
            file_path = os.path.join(BASE_DIR, relative_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Erreur suppression fichier : {e}")

        # 4. Supprimer l'entrée en base de données
        db.delete(item)
        db.commit()
        
        # 5. Retourner une réponse vide avec un code 200
        # HTMX verra le contenu vide et supprimera l'élément du DOM (hx-swap="outerHTML")
        return Response(status_code=200)
    
    return Response(status_code=404)

@app.post("/items/manual")
async def add_item_manual(
    request: Request,
    title: str = Form(...), # Ce champ pourra contenir soit le nom, soit l'URL
    price: str = Form(None),
    source_type: str = Form("manual"),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user = auth.get_current_user_from_cookie(request, db)
    
    # Détection automatique de lien Amazon
    if "amazon" in title.lower() and (title.startswith("http")):
        data = scrape_amazon(title)
        if data:
            new_item = models.Item(
                title=data["title"],
                price=data["price"],
                image_url=data["image_url"],
                product_url=data["product_url"],
                source_type="Amazon",
                user_id=user.id
            )
            db.add(new_item)
            db.commit()
            return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)