FROM ghcr.io/home-assistant/amd64-base:latest

# Installation de Python et des outils nécessaires
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    linux-headers

WORKDIR /app

# Copie et installation des dépendances
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copie du code applicatif
COPY app/ /app/

# Au lieu de COPY run.sh, on crée le script directement ici pour garantir le format Linux (LF)
RUN echo '#!/usr/bin/with-contenu-env bashio' > /launch.sh && \
    echo 'echo "-------------------------------------------------------"' >> /launch.sh && \
    echo 'echo "   _    _  _  _  _  _  _  _  _  _  _  _  _  _  _   "' >> /launch.sh && \
    echo 'echo "  | |  | |/ || || || || || || || || || || || |  "' >> /launch.sh && \
    echo 'echo "  | |  | | WATCHLISTERR - STARTING...          |  "' >> /launch.sh && \
    echo 'echo "  |_|  |_|_||_||_||_||_||_||_||_||_||_||_||_|_|  "' >> /launch.sh && \
    echo 'echo "-------------------------------------------------------"' >> /launch.sh && \
    echo 'python3 /app/main.py' >> /launch.sh && \
    chmod a+x /launch.sh

# On pointe sur le nouveau script généré proprement par Docker
CMD [ "/launch.sh" ]