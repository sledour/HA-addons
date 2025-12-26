# Utilisation de l'image de base Home Assistant (Builder compatible)
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

# On définit la version de Watchlistarr qu'on veut extraire
# On utilise le système multi-stage de Docker pour récupérer les fichiers proprement
COPY --from=nmarus/watchlistarr:latest /app /app

# Installation des dépendances pour faire tourner l'app (dotnet runtime est souvent requis pour les outils "Arr")
# Cependant, l'image nmarus est basée sur Alpine, on installe donc le nécessaire
RUN apk add --no-cache \
    icu-libs \
    krb5-libs \
    libgcc \
    libintl \
    libssl3 \
    libstdc++ \
    zlib \
    bash \
    curl \
    jq

# Copie du script de démarrage
COPY run.sh /
RUN chmod a+x /run.sh

# Watchlistarr s'attend à être dans /app
WORKDIR /app

ENTRYPOINT [ "/run.sh" ]
