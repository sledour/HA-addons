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

# Copie du script de lancement à la racine
COPY run.sh /run.sh
RUN chmod a+x /run.sh

# Nettoyage des caractères invisibles (Windows/Dos) au cas où
RUN sed -i 's/\r$//' /run.sh

WORKDIR /app
COPY app/ /app/

# On lance le script depuis la racine
CMD [ "/run.sh" ]