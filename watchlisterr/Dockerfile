FROM ghcr.io/home-assistant/amd64-base:latest

# Installation de Python et des outils système
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    linux-headers

WORKDIR /app

# Installation des dépendances Python
# On ajoute jinja2 explicitement au cas où il manque dans requirements.txt
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages \
    -r requirements.txt \
    jinja2 \
    python-multipart

# Copie de tout le dossier app (incluant templates/ et images)
COPY app/ /app/
COPY config.yaml /app/config.yaml

# Exécution
CMD ["python3", "/app/main.py"]