FROM ghcr.io/home-assistant/amd64-base:latest

# Installation explicite de Python3 et Pip3 via apk
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    linux-headers

# Création du dossier de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des librairies Python
# On utilise --break-system-packages car Alpine/HASS sont restrictifs
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copie du code source
COPY app/ /app/

# Script de lancement
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]