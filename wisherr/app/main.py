from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

# Charge les variables du fichier .env dans l'environnement
load_dotenv()

from . import models, auth, database

# Création des tables au démarrage
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Wisherr")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)