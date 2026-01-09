<p align="center">
  <img src="logo.png" alt="Watchlisterr Logo" width="200">
</p>

# 🎬 Watchlisterr

**Watchlisterr** est un agrégateur de listes de lecture (watchlists) pour l'écosystème Plex et Overseerr. Il permet de centraliser et d'afficher les films et séries que vos utilisateurs souhaitent regarder, tout en facilitant leur gestion.

## 🚀 Fonctionnalités

- 🔄 **Synchronisation Multi-Sources** : Récupère les watchlists depuis Plex et Overseerr.
- 🖼️ **Proxy d'images Intelligent** : Contourne les restrictions de sécurité (CORS) et les problèmes d'affichage dans Home Assistant Ingress grâce à un proxy local pour les posters TMDB.
- 👥 **Multi-Utilisateurs** : Gère plusieurs comptes et affiche qui a ajouté quel média.
- ⚡ **Base de données SQLite** : Mise en cache des informations (TMDB ID, posters, types) pour des performances optimales et limiter les appels API.
- 🎨 **Interface Moderne** : Dashboard responsive avec un mode sombre, utilisant Tailwind CSS.

## 🛠️ Installation (Add-on Home Assistant)

1. Ajoutez l'URL de ce dépôt à vos dépôts d'Add-ons Home Assistant.
2. Installez **Watchlisterr**.
3. Configurez les variables suivantes dans l'onglet **Configuration** :
   - `plex_url` & `plex_token`
   - `overseerr_url` & `overseerr_api_key`
   - `tmdb_api_key` (pour la récupération des posters)
4. Lancez l'Add-on.

## 🖥️ Aperçu technique

### Recherche et Précision
Le système utilise l'API `search/multi` de TMDB avec un algorithme de filtrage par ID et par année pour garantir que le poster affiché correspond exactement à la version du média présente dans votre liste (évite les erreurs sur les remakes ou les sagas).

### Proxy d'image
Pour garantir l'affichage des images dans l'interface de Home Assistant (souvent bloquées par les navigateurs pour des raisons de sécurité), Watchlisterr utilise une route interne :
`GET /proxy-image?url=https://image.tmdb.org/t/p/w500/path_to_image.jpg`

## ⚙️ Développement

### Structure du projet
- `main.py` : Serveur FastAPI et logique de synchronisation.
- `database.py` : Gestion de la base SQLite.
- `tmdb_api.py` : Interface avec l'API TheMovieDatabase.
- `templates/` : Interface utilisateur (Jinja2 + Tailwind).

### Logs de diagnostic
L'Add-on génère des logs détaillés pour suivre la synchronisation :
- `🔎 Recherche TMDB` : Identifie les nouveaux médias.
- `✅ Mis en cache` : Confirme l'enregistrement du poster et de l'ID.
- `📤 Requête` : Indique l'envoi d'une demande vers Overseerr.

---
*Développé pour simplifier la gestion de votre médiathèque personnelle.*

## 📌 À Faire (Roadmap)
- [ ] Ajouter une page secrete avec le contenue de la db user et media
- [ ] Ajouter une chips en haut a gauche des posters (logo plex mini = Dispo / logo Overseerr mini = En cours)
- [ ] Si dry_run off, pas d'affichage dans l'UI
- [ ] Stabiliser page web
- [ ] Activer l'envoi automatique des requêtes (Mode Production).