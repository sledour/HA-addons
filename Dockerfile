ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.20
FROM ${BUILD_FROM}

# Installation des dépendances système nécessaires
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers

# Dossier de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copie du code source
COPY app/ /app/

# Script de lancement obligatoire pour HASS
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]