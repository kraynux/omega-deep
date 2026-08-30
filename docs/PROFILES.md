# Profils de ports

Un profil est un nom associé à une liste de ports à scanner. Deux origines :

- **Système** (`origin = "system"`) : fournis avec l'outil, lecture seule, définis dans `domain/profiles/defaults.py`.
- **Utilisateur** (`origin = "user"`) : créés/modifiés/supprimés via `omega-deep profile ...`, persistés en JSON (`var/user_profiles.json` par défaut — chemin runtime ancré sur le dossier du projet, `$OMEGA_DEEP_VAR_DIR` pour le surcharger).

Un profil utilisateur ne peut pas porter le nom d'un profil système (noms réservés, voir `domain/profiles/policies.py::ensure_name_not_reserved`). `domain/profiles/` est identique à omega-check (D-005) — aucune divergence de modèle ou de règle de validation.

## Profils système

| Nom | Description | Épinglé |
|---|---|---|
| `minimal` | Scan ultra-rapide : SSH + HTTP + HTTPS (22, 80, 443) | oui |
| `classic` | Services classiques Internet/LAN | oui |
| `web` | Services web et alternatives (80, 443, 8000-10443) | non |
| `db` | Bases de données et services de données (MySQL, PostgreSQL, MongoDB, Redis, etc.) | non |
| `remote` | Accès distants — shell, bureau, RustDesk | non |
| `mail` | Services de messagerie (SMTP, IMAP, POP3) | non |
| `dns` | Services DNS (53, 853, 5353) | non |
| `iot` | Équipements IoT, caméras, box, domotique | non |
| `dev` | Environnements de développement/lab | non |
| `docker` | Docker, Swarm et services courants en conteneurs | non |
| `complet` | **Généré dynamiquement** : union triée et dédupliquée de tous les profils ci-dessus | non |

`complet` n'existe pas comme entrée statique : `domain/profiles/defaults.py::build_complete_profile()` le recalcule à chaque appel à partir des profils système ci-dessus, pour rester automatiquement à jour si un profil système évolue.

## Un seul profil pour toute l'analyse

Contrairement à omega-check (qui scanne une cible unique), une analyse DEEP scanne potentiellement plusieurs hosts — la cible racine, puis chaque cible découverte acceptée. **Le même profil s'applique à tous** : il n'existe pas de mécanisme pour scanner la racine avec un profil et les cibles découvertes avec un autre. Ce choix évite un risque bien réel — une cible découverte scannée avec un profil "plus large" que celui explicitement choisi par l'utilisateur pour l'analyse, sans qu'il l'ait demandé.

Une conséquence pratique : `omega-deep analyze <cible>` ne connaît qu'un profil par **nom** (`--profile`), jamais une liste de ports ad-hoc — nécessaire pour pouvoir rejouer une analyse à l'identique depuis l'historique (`domain/scans/models.py::Scan.profile_name`). Un besoin de ports personnalisés passe donc toujours par un profil utilisateur nommé (voir ci-dessous), pas par une saisie libre au moment de lancer l'analyse.

## Gestion des profils utilisateur

```bash
omega-deep profile list
omega-deep profile create <nom> --ports <p1,p2,...> [--description <texte>] [--pin]
omega-deep profile edit <nom> [--description <texte>] [--ports <p1,p2,...>]
omega-deep profile delete <nom>
omega-deep profile pin <nom>
omega-deep profile unpin <nom>
```

En TUI, les mêmes opérations sont disponibles depuis l'écran **Profils** (menu principal) ; les profils personnels apparaissent ensuite dans le sélecteur de profil de l'écran **Analyser**, préfixés `* ` pour les distinguer des profils système.

Règles de validation (`domain/profiles/policies.py`) :

- Chaque port doit être compris entre 1 et 65535.
- Pas de doublons dans la liste de ports d'un même profil.
- Le nom ne doit pas être un nom de profil système (ni `complet`).

`pin`/`unpin` ne s'appliquent qu'aux profils utilisateur : le statut épinglé d'un profil système est fixé une fois pour toutes dans `defaults.py`, il ne se persiste pas.
