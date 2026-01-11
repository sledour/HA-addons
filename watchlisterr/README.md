<p align="center">
  <img src="https://raw.githubusercontent.com/sledour/HA-addons/main/watchlisterr/logo.png" alt="Watchlisterr Logo" width="200">
</p>

<p align="center">
  <strong>L'agrégateur de Watchlists ultime pour Plex & Overseerr</strong>
</p>

---

Watchlisterr est un pont intelligent entre votre Watchlist Plex et vos outils de téléchargement (Overseerr/Radarr/Sonarr).

Il permet de transformer l'ajout d'un film ou d'une série dans votre liste de favoris Plex en une requête automatique de contenu, tout en offrant un tableau de bord visuel pour suivre l'état de vos demandes.

🎯 Le But
Simplifier la gestion des médias pour vous et vos utilisateurs. Plus besoin d'ouvrir plusieurs applications :

Vous parcourez Plex, vous voyez un film qui vous tente.

Vous cliquez sur "Ajouter à la Watchlist".

Watchlisterr le détecte, l'envoie à Overseerr, et vous informe quand il est prêt sur votre serveur.

⚙️ Configuration
L'outil se configure via quelques options simples :

Plex URL & Token : Pour lire les listes de favoris de vos utilisateurs.

Overseerr URL & API Key : Pour envoyer les demandes de téléchargement.

TMDB API Key : Pour récupérer les superbes affiches (posters) et les détails des films.

Intervalle de synchronisation : Fréquence à laquelle l'outil vérifie vos listes (ex: toutes les 3 minutes).

Mode Simulation (Dry Run) : Permet de tester l'outil sans envoyer de vraies requêtes.

📊 Le Dashboard
Le tableau de bord intégré vous permet de :

Voir tous les films demandés par vos amis.

Filtrer par état : Non demandé, En cours (Logo Overseerr) ou Disponible (Logo Plex).

Lancer une synchronisation manuelle d'un simple clic.
