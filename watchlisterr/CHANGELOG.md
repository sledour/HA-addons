# Journal des modifications (Changelog)

---

## [1.0.0] - 2026-01-11
### ✨ Version Stable Finale
Cette version marque la sortie officielle de Watchlisterr en version 1.0.0, incluant une gestion d'état robuste et une interface utilisateur complète.

### 🚀 Nouvelles Fonctionnalités
- **Système de Status Unifié** : Implémentation du système de codes numériques (`0: Absent`, `1: Sur Plex`, `2: En cours Overseerr`) pour une synchronisation sans faille entre la base de données et l'interface.
- **Persistance de Statut** : Le flag de requête Overseerr est désormais sauvegardé en base de données, permettant un affichage immédiat même après un redémarrage.
- **Priorisation Intelligente** : Si un média est détecté sur Plex, le statut "Disponible" (Code 1) prend automatiquement le dessus sur le statut "En cours".

### 🛠️ Améliorations & Fixes
- **Fiabilité UI** : Correction définitive du bug qui empêchait l'affichage des logos orange (Overseerr) sur le Dashboard.
- **Optimisation DB** : Migration de la table `media_cache` pour supporter les nouveaux codes d'état.
- **Journalisation** : Amélioration de la clarté des logs lors de la détection des statuts via Overseerr.

---

## [0.3.5] - 2026-01-08
### 🖥️ Dashboard & Backend
- **Interface Web** : Déploiement du tableau de bord FastAPI avec rafraîchissement des statuts.
- **Mapping Utilisateurs** : Synchronisation automatique des comptes Plex et Overseerr basée sur le nom d'utilisateur.
- **Proxy d'Images** : Mise en place d'un proxy pour l'affichage sécurisé des posters TMDB.

---

## [0.1.0] - 2026-01-02
### Initialisation
- Première version fonctionnelle du script de synchronisation.
- Support de la Watchlist administrateur et des APIs de base.