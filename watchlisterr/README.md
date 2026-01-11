<p align="center">
  <img src="https://raw.githubusercontent.com/sledour/HA-addons/main/watchlisterr/logo.png" alt="Watchlisterr Logo" width="200">
</p>

<p align="center">
  <strong>L'agrégateur de Watchlists ultime pour Plex & Overseerr</strong>
</p>

---

![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/Status-Stable-success.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)

**Watchlisterr** est un pont intelligent entre votre **Watchlist Plex** et votre outil de gestion de requêtes (**Overseerr**). 

Il automatise le processus de demande de contenu : transformez un simple ajout en "favori" sur Plex en une requête réelle sur votre infrastructure de téléchargement, tout en offrant un tableau de bord visuel pour suivre l'état de vos demandes.

---

## 🎯 Le Concept
Simplifiez la vie de vos utilisateurs et la vôtre. Plus besoin de jongler entre plusieurs applications :

1.  **Parcourez Plex** : Trouvez un film ou une série qui vous tente.
2.  **Ajoutez à la Watchlist** : Cliquez simplement sur le bouton "Ajouter à la Watchlist" (l'icône drapeau).
3.  **Automatisation** : **Watchlisterr** détecte l'ajout, crée la requête sur Overseerr, et suit l'état d'avancement jusqu'à la disponibilité sur votre serveur.

---

## 📊 Le Dashboard
L'interface web intégrée vous permet de superviser toute l'activité de votre serveur en un clin d'œil :

* **Vue unifiée** : Visualisez tous les médias présents dans les Watchlists de vos utilisateurs.
* **Indicateurs d'état visuels** :
    * 🏷️ **Non demandé** : Le média est dans une liste mais n'a pas encore fait l'objet d'une requête.
    * 🟠 **En cours** : La requête est approuvée et le téléchargement est géré par Overseerr (Logo Overseerr présent).
    * 🟢 **Disponible** : Le média est prêt à être visionné sur votre serveur (Logo Plex présent).
* **Contrôle Total** : Forcez une synchronisation manuelle et consultez les journaux d'activité (Logs) en temps réel directement sur la page.



---

## ⚙️ Configuration
L'outil se configure via des options simples et explicites :

| Paramètre | Description |
| :--- | :--- |
| **Plex URL & Token** | Permet de lire les listes de favoris de vos utilisateurs. |
| **Overseerr API** | URL et clé API pour l'envoi et le suivi des requêtes. |
| **TMDB API Key** | Récupération des affiches (posters) et métadonnées des médias. |
| **Sync Interval** | Fréquence de vérification des listes (ex: toutes les 3 minutes). |
| **Mode Simulation** | (Dry Run) Permet de tester l'outil sans envoyer de vraies requêtes. |

---

## 🖼️ Aperçu
> **Astuce** : Pour insérer une capture d'écran ici, glissez-déposez simplement votre image dans l'éditeur GitHub lors de la modification de ce fichier.

---

## 🚀 Utilisation
1. Configurez vos accès dans les options.
2. Lancez l'application.
3. Accédez au tableau de bord via `http://VOTRE_IP:1604`.

---
*Développé pour améliorer l'écosystème Plex automatisé.*
