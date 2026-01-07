# Utilisation de l'image de base Python officielle de Home Assistant
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.20
FROM ${BUILD_FROM}

# Installation des dépendances système (nécessaires pour compiler certaines libs Python si besoin)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers

# Dossier de travail
WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copie du code source (le dossier app doit être au même niveau que le Dockerfile)
COPY app/ /app/

# Script de lancement
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]