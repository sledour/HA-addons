ARG BUILD_FROM
FROM $BUILD_FROM

# Installation des dépendances si nécessaire
RUN apk add --no-cache jq

# Utilise l'image officielle de Watchlistarr comme source de binaires ou de fichiers
# Ou installe directement l'application
# Ici, on suppose qu'on lance le container officiel adapté à HA
# Vous pouvez aussi faire un FROM direct si vous ne voulez pas utiliser le build système de HA :
FROM nmarus/watchlistarr:latest

# Copie du script de lancement
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
