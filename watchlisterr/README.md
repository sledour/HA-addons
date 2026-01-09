# 🎬 Watchlisterr for Home Assistant

**Watchlisterr** est un add-on pour Home Assistant qui synchronise les Watchlists Plex (Admin et Amis) avec Overseerr. Il utilise TMDB comme agent de liaison pour garantir une correspondance parfaite des médias, même lorsque les métadonnées Plex sont incomplètes.

---

## 🚀 État Actuel : Mode "Dry Run"
L'add-on est actuellement en **phase de monitoring**. Il analyse les watchlists et génère un rapport JSON complet, mais **n'effectue aucune requête automatique** sur Overseerr pour le moment.

## 🛠️ Fonctionnement Technique
1. **Plex API** : Récupère les watchlists de l'administrateur et de tous les amis connectés.
2. **TMDB API** : Convertit les titres et années en IDs TMDB uniques et corrige les types (ex: détecte si un contenu est une série ou un film).
3. **Overseerr API** : Vérifie le statut de chaque ID TMDB (Disponible, Demandé, ou Non présent).

## 📂 Structure du Projet
* `app/main.py` : Cœur de l'application et serveur FastAPI.
* `app/plex_api.py` : Gestion des appels vers Plex (Profil, Amis, Watchlists).
* `app/overseerr_api.py` : Communication avec Overseerr (Statuts, Utilisateurs).
* `app/tmdb_api.py` : Agent de résolution pour les IDs TMDB.
* `config.yaml` : Configuration de l'add-on pour Home Assistant.

---

## ⚙️ Configuration
Pour fonctionner, l'add-on nécessite les options suivantes dans Home Assistant :

| Option | Description |
| `plex_token` | Ton jeton d'authentification Plex. |
| `plex_server_url` | URL locale de ton serveur Plex (ex: http://192.168.x.x:32400). |
| `overseerr_url` | URL de ton instance Overseerr. |
| `overseerr_api_key` | Clé API récupérée dans les réglages d'Overseerr. |
| `tmdb_api_key` | Clé API v3 de The Movie Database. |

---

## 📊 Visualisation des données
Une fois l'add-on lancé, les données sont accessibles via Ingress

### Exemple de stats générées :
* **total_plex** : Nombre total d'items suivis.
* **already_on_plex** : Items déjà disponibles sur ton serveur.
* **to_overseerr** : Items identifiés comme "Non demandés" et prêts pour une future automatisation.

---

## 📌 À Faire (Roadmap)
- [x] Mapper les utilisateurs Plex avec les IDs utilisateurs Overseerr.
- [x] Création d'une base de donnée poursauvegarder le cache (mapping des users et média à envoyer vers Overseerr)
- [ ] Ajout d'un scan_interval pour les watchlists et users
- [ ] Créer une interface Web visuelle (Posters de films demandés a Overseerr).
- [ ] Activer l'envoi automatique des requêtes (Mode Production).