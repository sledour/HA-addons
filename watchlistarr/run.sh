#!/usr/bin/env bashio
set -e

bashio::log.info "Démarrage de Watchlistarr..."

# Récupération des options de HA
export PLEX_TOKEN=$(bashio::config 'PLEX_TOKEN')
export PLEX_SERVER=$(bashio::config 'PLEX_SERVER')
export RADARR_URL=$(bashio::config 'RADARR_URL')
export RADARR_API_KEY=$(bashio::config 'RADARR_API_KEY')
export SONARR_URL=$(bashio::config 'SONARR_URL')
export SONARR_API_KEY=$(bashio::config 'SONARR_API_KEY')
export INTERVAL=$(bashio::config 'INTERVAL')
export PORT=$(bashio::config 'PORT')
export LOG_LEVEL=$(bashio::config 'LOG_LEVEL')

exec /app/watchlistarr
