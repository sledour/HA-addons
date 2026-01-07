#!/usr/bin/with-contenu-env bashio

echo "-------------------------------------------------------"
echo "                WATCHLISTERR ADDON                     "
echo "                                                        "
echo "                VERSION: 0.0.1                          "
echo "-------------------------------------------------------"

# Récupération des options pour le log de démarrage
OVERSEERR_URL=$(bashio::config 'overseerr_url')
echo "[INFO] Connexion cible : $OVERSEERR_URL"
echo "[INFO] Port d'écoute Ingress : 1604"
echo "-------------------------------------------------------"

# Lancement de l'application
exec python3 /app/main.py