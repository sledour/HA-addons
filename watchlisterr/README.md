<p align="center">
  <img src="https://raw.githubusercontent.com/sledour/HA-addons/main/watchlisterr/logo.png" alt="Watchlisterr Logo" width="200">
</p>

<p align="center">
  <strong>L'agrégateur de Watchlists ultime pour Plex & Overseerr</strong>
</p>

---

**Watchlisterr** centralise les listes de lecture de vos utilisateurs Plex et synchronise vers Overseerr

## 🚀 Points forts

* 🔄 **Synchronisation Automatique** : Scan cyclique de Plex et Overseerr.
* 🎯 **Précision TMDB** : Filtrage par ID unique pour éviter les erreurs de posters sur les remakes.
* 🛡️ **Image Proxy** : Système intégré pour contourner les blocages d'affichage (CORS) sous Home Assistant Ingress.
* 👥 **Multi-User** : Identification claire du demandeur pour chaque média.
* ⚡ **Ultra-Rapide** : Cache local SQLite pour un chargement instantané.

## 🛠️ Configuration

Une fois l'Add-on installé, renseignez les clés suivantes :

| Clé | Description |
| :--- | :--- |
| `plex_token` | Votre jeton d'authentification Plex. |
| `overseerr_api_key` | Clé API disponible dans les réglages Overseerr. |
| `tmdb_api_key` | Clé API (v3) de TheMovieDatabase. |

## 🏗️ Architecture
L'application repose sur un backend **FastAPI** qui pilote la logique de synchronisation en arrière-plan, tandis que le frontend en **Jinja2/Tailwind** assure une présentation élégante des posters récupérés.

## 📌 À Faire (Roadmap)
- [ ] Ajouter une chips en haut a gauche des posters (logo plex mini = Dispo / logo Overseerr mini = En cours)
- [ ] Si dry_run off, pas d'affichage dans l'UI
- [ ] Ajout d'un filtre (à coté de Watchlist) pour filtrer par users/etat (Plex ou Overseerr) et type (movie/tv)
- [ ] Stabiliser page web
- [ ] Activer l'envoi automatique des requêtes (Mode Production).
