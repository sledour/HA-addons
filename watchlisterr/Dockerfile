FROM ghcr.io/home-assistant/amd64-base:latest

# Installation de Python et Pip
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    linux-headers

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copie du code
COPY app/ /app/

# Au lieu d'un script externe, on demande à HASS de lancer directement Python
# On utilise la forme "exec" pour que S6 puisse le gérer
CMD ["python3", "/app/main.py"]