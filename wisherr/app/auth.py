from passlib.context import CryptContext
from fastapi import Request
from sqlalchemy.orm import Session
from . import models

# Configuration du hachage (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_session_cookie(response, username: str):
    # Pour un MVP, on stocke le username dans le cookie (signé ou non)
    # Dans une app pro, on utiliserait un JWT ou un ID de session en DB
    response.set_cookie(key="wisherr_session", value=username, httponly=True)

def get_current_user_from_cookie(request: Request, db: Session):
    username = request.cookies.get("wisherr_session")
    if not username:
        return None
    return db.query(models.User).filter(models.User.username == username).first()