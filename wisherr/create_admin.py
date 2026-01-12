from app.database import SessionLocal, engine
from app.models import Base, User
from app.auth import get_password_hash

# Créer les tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

db = SessionLocal()
admin_user = db.query(User).filter(User.username == "admin").first()

if not admin_user:
    new_user = User(
        username="admin",
        hashed_password=get_password_hash("Passw0rd!")
    )
    db.add(new_user)
    db.commit()
    print("Utilisateur admin créé avec succès !")
else:
    print("L'utilisateur admin existe déjà.")
db.close()