from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# On charge le .env ici aussi pour être sûr que DATABASE_URL soit lu
load_dotenv()

# Priorité au .env, sinon dossier /data (HA), sinon local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wisherr.db")

# check_same_thread=False est requis uniquement pour SQLite
# On peut ajouter un petit check pour ne l'activer que si c'est du sqlite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()