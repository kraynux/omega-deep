<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->
<div align="center">
  <img src="docs/assets/omega-deep.png" alt="Omega-Deep" width="384">
</div>

# 🖧 OMEGA-DEEP

**Analyse d'architecture multi-cibles (découverte + garde-fous + graphe)**

> Élaboré par [kraynux](https://github.com/kraynux) pour [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Page officiel : [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Apercu : [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface et rapports exportés disponibles en **17 langues** — voir [Langues de l'interface](#langues-de-linterface).  
**Langues :**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](docs/translation/en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](docs/translation/es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](docs/translation/pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](docs/translation/it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](docs/translation/de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](docs/translation/nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](docs/translation/pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](docs/translation/ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](docs/translation/zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](docs/translation/vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](docs/translation/th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](docs/translation/id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](docs/translation/ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](docs/translation/ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](docs/translation/hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](docs/translation/ar/README.md)

---

**Omega-deep** reprend tout ce que fait `omega-check` sur une cible unique (scan de ports, identification de service, rôles, WAF, TLS) et y ajoute la **découverte de cibles supplémentaires** à partir des indices laissés par la cible déjà scannée (en-têtes, redirections, certificat, liens HTML), sous des **garde-fous stricts** et une **validation utilisateur explicite** avant tout scan d'une cible découverte, puis **reconstruit un graphe d'architecture** (qui parle à qui, avec quelle confiance). Outil de la suite `omega-`, structuré en Clean Architecture — voir `docs/ARCHITECTURE.md` pour le détail technique complet.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-deep/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-deep/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-deep/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-deep/D.png" width="24%" />
</p>

## 1. Vision et périmètre

Omega-deep répond à une question qu'omega-check ne pose pas : *derrière cette IP, qu'est-ce qu'il y a d'autre ?* Un reverse-proxy qui annonce son backend, un certificat qui couvre plusieurs hôtes, une page qui pointe vers un service voisin — autant d'indices qu'omega-deep suit, prudemment, jamais tout seul.

### Ce que fait Omega-deep

- Scanne une cible racine exactement comme omega-check (profil système, ou profil personnel enregistré).
- Découvre des cibles candidates à partir des indices laissés par chaque host déjà scanné : en-têtes HTTP (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), redirection (`Location`), certificat TLS (SAN), liens HTML — voir [§4](#4-découverte-de-cibles-et-garde-fous).
- Ne scanne **jamais** une cible découverte sans validation explicite, cible par cible — le silence n'est jamais une acceptation.
- Borne la découverte par des garde-fous stricts : profondeur maximale, nombre maximal de cibles supplémentaires, sous-réseau autorisé (même plage privée que la racine par défaut).
- Reconstruit un **graphe d'architecture** à partir de la provenance de chaque cible acceptée (`proxy_to`, `redirect_to`, `linked_to`), avec un niveau de confiance par relation — voir [§8](#8-graphe-darchitecture).
- Restitue le résultat en TUI (Textual) ou en CLI scriptable, avec les mêmes trois exports qu'omega-check (JSON, texte, HTML 5 thèmes) — le graphe y est un **vrai diagramme dessiné** en HTML, pas un tableau.
- Qualifie chaque information collectée (service comme découverte) d'un niveau de confiance explicite — voir [§9](#9-politique-de-confiance).
- Conserve un historique persistant des analyses, rejouable et comparable dans le temps.

### Ce qu'Omega-deep ne fait pas

- Scan de vulnérabilités actives, pas de SQLi, XSS ou RCE.
- Scan de CVE.
- Prise d'empreinte du système d'exploitation.
- Techniques de scan bas niveau façon nmap (SYN scan, paquets bruts) — connexion TCP applicative uniquement.
- Outil de bruteforce ou de fuzzing.
- Scan d'une cible découverte sans confirmation explicite de l'utilisateur — jamais, sous aucun mode.
- Découverte au-delà du sous-réseau privé de la cible initiale, sauf configuration explicite (`--subnet`).
- Dashboard web.

## 2. Installation

### Prérequis

- Python 3.10+
- Connexion Internet, pour les dépendances

### Installation

```bash
[ -d omega-deep ] && echo "ℹ️ Déjà extrait ici, étape ignorée." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh` :

1. Crée l'environnement virtuel `.venv` s'il n'existe pas déjà.
2. Installe les dépendances (`vendor/omega-lib/` puis `pip install -e .`, `pyproject.toml` reste l'unique source de vérité).
3. Rend `omega-deep.sh` et `install.sh` exécutables.
4. Ajoute l'alias `deep` à `~/.bashrc` et `~/.zshrc` (sans doublon si déjà présent).

### Dépendances

Déclarées dans `pyproject.toml` (plus de `requirements.txt`) :
- `omega-lib` : bibliothèque partagée de la suite (`ConfidenceLevel`, thèmes, détection de terminal) — vendorisée dans `vendor/omega-lib/`
- `textual` : interface TUI, thèmes, adaptation automatique au terminal
- `httpx` : sondes HTTP/HTTPS (service et découverte)
- `cryptography` : lecture du certificat TLS négocié
- `jinja2` : templating pour l'export HTML
- Dépendances de développement (`pip install -e ".[dev]"`) : `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Utilisation

### Mode interactif (TUI)

Recommandé pour l'usage quotidien — lancé sans argument :

```bash
./omega-deep.sh
```
si vous avez créé l'alias, tapez juste `deep` dans le terminal :
```bash
deep
```

Parcours : écran de démarrage (se ferme sur une touche ou un clic) → menu principal (Analyser / Profils / Historique / Réglages / Aide) → saisie de la cible racine, choix du profil et des garde-fous de découverte (profondeur max, nombre max de cibles, sous-réseau autorisé) → analyse (jauge indéterminée et déroulé des opérations réseau en direct) → à chaque lot de cibles découvertes, écran de validation (une ligne par cible, source/confiance/preuve affichées, bascule accepter/refuser — aucune case cochée par défaut) → détail de l'analyse (hosts, ports/services/rôles, graphe, export) → historique/comparaison/rejeu et réglages depuis le menu principal. L'adaptation au terminal (couleurs, taille, dégradation structurelle) est automatique.

#### Raccourcis clavier

| Touche | Action |
|---|---|
| `↑` / `↓` | Naviguer entre les éléments d'un écran |
| `Tab` / `Maj+Tab` | Naviguer entre les champs d'un formulaire |
| `Échap` | Retour à l'écran précédent (confirmation de sortie sur l'accueil) |
| `t` | Thème suivant (appliqué immédiatement, sans confirmation) |
| `r` | Rafraîchir la détection du terminal |
| `a` | Afficher l'aide |
| `q` | Quitter (avec confirmation) |

### Langues de l'interface

L'interface est disponible en 17 langues : français, anglais, espagnol, portugais (Brésil), italien, allemand, néerlandais, polonais, russe, chinois simplifié, vietnamien, thaï, indonésien, japonais, coréen, hindi et arabe. Le choix se fait dans les Réglages (« Langue / Language ») et s'applique après un redémarrage de l'interface ; la variable `OMEGA_DEEP_LANG` (par exemple `OMEGA_DEEP_LANG=en ./omega-deep.sh`) force une langue le temps d'une session. Lancé depuis omega-suite, omega-deep prend la langue de la suite. Sur une console texte Linux (TTY), les langues à écriture non latine s'affichent en anglais pour la session. La ligne de commande reste en français.

### Contact et support

L'aide (touche `a`) propose un écran **Contact et support** : *Payer un café* (page PayPal du développeur), *Contacter le support* (adresse mail et formulaire de contact du site, affichés en clair), *Se déclarer utilisateur (anonyme)* et *Vérifier les mises à jour*. La déclaration est volontaire, désactivée par défaut et envoyée une seule fois : elle sert seulement à compter les utilisateurs et, si on le souhaite, leur continent ou leur pays (listes fermées, jamais de texte libre). Elle envoie une clé tirée au hasard, le nom du logiciel (`omega-deep`) et sa version ; jamais de nom, de nom de machine, de réglage, de cible ni de résultat. L'adresse IP n'est pas enregistrée dans les déclarations, mais passe, comme toute visite, par les contrôles de sécurité et le journal du serveur de réception. Retrait à tout moment depuis le même écran (*Ne plus me déclarer*). La vérification des mises à jour lit seulement la liste des versions publiées sur le site, et jamais sans clic.

### Mode scriptable (CLI)

Toute sous-commande déclenche le mode CLI :

```bash
# Analyser une cible (scan racine + découverte multi-cibles)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# Historique (filtrable par cible racine)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Détail d'une analyse (texte, JSON ou HTML) — 5 thèmes d'export au choix
./omega-deep.sh show <scan_id> --format html --theme omega-base --output rapport.html

# Comparer deux analyses (état des ports de la cible racine)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Profils de ports personnels
./omega-deep.sh profile list
./omega-deep.sh profile create labo --ports 22,80,443 --description "Mon profil"
./omega-deep.sh profile edit labo --ports 22,80,443,8080
./omega-deep.sh profile pin labo
./omega-deep.sh profile unpin labo
./omega-deep.sh profile delete labo
```

En CLI, la validation des cibles découvertes se fait par une question interactive par cible (`Scanner <cible> ? [o/N]`), avec le détail de la preuve affiché avant chaque question. `--auto-validate` accepte tout sans revue (**déconseillé**, avertissement affiché) ; en environnement non-interactif (pas de TTY, `--auto-validate` absent), toute cible découverte est rejetée par défaut plutôt que scannée sans confirmation.

### Formats de cible acceptés

```text
192.168.1.10                IPv4
example.org                 Hostname
http://example.org          URL HTTP  (schéma retiré avant résolution)
https://example.org:8443    URL HTTPS avec port  (schéma et port retirés)
```

Le schéma et le port éventuels sont retirés avant résolution DNS (`domain/targets/validation.py::normalize_target_input`) — coller une URL entière fonctionne, seul l'hôte est conservé. Les cibles *découvertes*, elles, sont normalisées de la même façon mais ne sont jamais scannées sans validation (voir [§4](#4-découverte-de-cibles-et-garde-fous)).

## 4. Découverte de cibles et garde-fous

### Sources d'indices

| Source | Origine | Confiance |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | En-tête `Location` d'une réponse HTTP | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) du certificat TLS négocié | `DECLARED` |
| `html_link` | Liens (`<a href>`) servis par la page | `INFERRED` |

Une valeur `DECLARED` reste une auto-déclaration de la cible (falsifiable) — voir [§10](#10-protection-contre-les-valeurs-falsifiées). `html_link` est volontairement la source la plus faible : un simple lien ne déclare aucune relation d'infrastructure.

### Garde-fous (toujours actifs, jamais désactivables)

- **Périmètre** : une cible candidate doit être une IP privée dans le même `/24` que la cible racine, sauf `--subnet` explicite (auquel cas seule l'appartenance au sous-réseau donné compte, y compris s'il couvre des IPs publiques — c'est la configuration explicite qui autorise l'exception). Un hostname non résolu n'est jamais accepté par ce filtre (résoudre pour vérifier serait déjà une action réseau hors de la portée de cette vérification).
- **Profondeur** : `--max-depth` (défaut 3) — A → B → C → D maximum.
- **Nombre de cibles** : `--max-targets` (défaut 10) — toutes profondeurs confondues.

### Validation (jamais de scan sans confirmation)

Chaque cible proposée suit `PROPOSED → PRESENTED → ACCEPTED` ou `REJECTED`. La règle est **fail-safe** : toute cible jamais explicitement acceptée (silence, fermeture d'écran, interruption, timeout, absence de TTY) est traitée comme refusée — jamais l'inverse. En TUI, un écran dédié liste les cibles d'un lot avec preuve et confiance, bascule accepter/refuser par ligne, "tout accepter"/"tout rejeter", et un rejet total par défaut sur Échap. En CLI, une question par cible ; `--auto-validate` (déconseillé) est la seule façon de contourner l'interactivité.

## 5. Profils de scan

| Profil | Description | Épinglé |
|---|---|---|
| `minimal` | Scan ultra-rapide : SSH + HTTP + HTTPS (22, 80, 443) | oui |
| `classic` | Services classiques Internet/LAN | oui |
| `web` | Services web et alternatives | non |
| `db` | Bases de données et services de données | non |
| `remote` | Accès distants — shell, bureau, RustDesk | non |
| `mail` | Services de messagerie | non |
| `dns` | Services DNS | non |
| `iot` | Équipements IoT, caméras, box, domotique | non |
| `dev` | Environnements de développement/lab | non |
| `docker` | Docker, Swarm et services courants en conteneurs | non |
| `complet` | **Généré à la volée** : union triée et dédupliquée de tous les profils ci-dessus | non |
| *profil personnel* | Créé dans l'écran **Profils** (TUI) ou `profile create` (CLI), listé au même endroit que les profils système, préfixé `* ` en TUI | non |

Le profil s'applique à la cible racine **et** à chaque cible découverte acceptée — pas de profil différent par host. Détail complet, règles de validation et gestion des profils personnels : `docs/PROFILES.md`.

## 6. Architecture

Omega-deep est structuré en **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), alignée sur le gabarit de la suite `omega-` (voir `omega-scan`/`omega-check`) et vérifiée par `import-linter` à chaque modification. Le détail complet vit dans **`docs/ARCHITECTURE.md`**.

Vue d'ensemble très courte :

```text
src/omega_deep/
├── domain/          Logique métier pure : scans, cibles, services, profils, rapports,
│                    discovery (cibles proposées, machine à états de validation),
│                    architecture (graphe, règles de relation)
├── application/     Cas d'usage (commands/queries) — dont discover_targets,
│                    validate_targets, reconstruct_architecture (nouveaux vs. omega-check)
├── ports/           Contrats attendus par l'application (probers, dont discovery_prober,
│                    repositories, exporters...)
├── infrastructure/  Implémentations concrètes (socket/httpx/cryptography, SQLite,
│                    rendu SVG du graphe — Textual n'est PAS ici)
├── interfaces/      tui/ (Textual) et cli/ (scriptable), à parité fonctionnelle stricte
├── app/             Assemblage (DependencyContainer, bootstrap, cycle de vie)
├── core/, shared/   Vocabulaire transverse, utilitaires non métier
└── plugins/         Structure posée, vide (aucun axe d'extension confirmé)
```

Règles de conception :
- `domain/services/policies.py` : classifie les indices déjà collectés, ne fait jamais de réseau.
- `domain/discovery/policies.py` : garde-fous de périmètre/profondeur/nombre — pure logique, testable sans réseau.
- `domain/architecture/service.py` : reconstruit le graphe depuis la provenance déjà portée par chaque `Host`, ne refait aucune requête.
- `infrastructure/network/` et `infrastructure/discovery/` : font du réseau (sockets, `httpx`, `cryptography`), ne jugent jamais.
- `interfaces/` : affiche, ne contient aucune logique métier — l'écran de validation des cibles découvertes appelle `validate_targets`, il n'implémente pas la règle fail-safe lui-même.
- `infrastructure/exporters/` : lisent le résultat d'analyse (scan, hosts, graphe), ne recalculent rien.

## 7. Identification de service et rôles

### Protocoles détectés

| Protocole | Sonde | Détail collecté |
|---|---|---|
| HTTP / HTTPS | `httpx` | Bannière `Server`, en-têtes d'authentification |
| TLS | `cryptography` (certificat négocié, `CERT_NONE` inclus) | Version, cipher, sujet/émetteur du certificat |
| SSH | Bannière brute | Logiciel et version (ex. `OpenSSH 10.4`) |
| VNC (RFB) | Codes de sécurité annoncés par le serveur | Types d'authentification supportés |
| Générique | Bannière brute sur port ouvert non reconnu | Extraction prudente, pas d'heuristique agressive |

### Rôles inférés

Déduits du protocole **réellement négocié**, jamais d'une supposition de numéro de port :

| Rôle | Condition | Confiance |
|---|---|---|
| `serveur web` | Protocole HTTP/HTTPS confirmé | `INFERRED` |
| `accès shell` | Protocole SSH confirmé | `CORROBORATED` |
| `accès graphique` | Protocole VNC confirmé | `CORROBORATED` |
| `base de données` | Port dans la plage du profil système `db` | `INFERRED` |

### Signatures WAF connues

Détectées via en-tête déclaratif (`server`, `x-sdk`) — présence **déclarée par la cible**, jamais vérifiée indépendamment : Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (répertorié à titre indicatif, pas un WAF applicatif à proprement parler).

## 8. Graphe d'architecture

Reconstruit uniquement à partir de la provenance déjà portée par chaque host accepté (`discovered_from`/`discovery_source`/`discovery_confidence`) — aucune nouvelle requête réseau, aucune re-analyse des indices bruts.

### Relations produites

| Relation | Source de découverte | Signification |
|---|---|---|
| `proxy_to` | `header` | La cible racine (ou un host déjà accepté) est vraisemblablement un proxy vers la cible découverte |
| `redirect_to` | `redirection` | Redirection HTTP observée vers la cible découverte |
| `linked_to` | `certificate` ou `html_link` | Relation la plus neutre — infrastructure/application partagée, sans direction de flux affirmée |

`backend_of` (l'arête inverse d'un `proxy_to`) n'est volontairement pas produit — ce serait un doublon d'information, pas une nouvelle déduction.

### Rendu

- **TUI** (détail d'une analyse) et **exports JSON/texte** : liste des arêtes (source, relation, cible, confiance) — un terminal n'est pas l'endroit pour un rendu graphique riche.
- **Export HTML** : un **vrai diagramme SVG** (nœuds = cercles, aretes = flèches étiquetées), mise en page en couches calculée depuis la cible racine, taille proportionnelle au nombre de machines découvertes — jamais de dépendance de layout de graphe lourde, le graphe reste petit par construction (borné par les garde-fous du [§4](#4-découverte-de-cibles-et-garde-fous)).

## 9. Politique de confiance

Chaque champ collecté porte un niveau parmi :

| Niveau | Signification |
|---|---|
| `VERIFIED` | Fait protocolaire observé directement, non falsifiable par la cible (ex : port fermé confirmé par RST TCP, version TLS réellement négociée). |
| `DECLARED` | Valeur auto-annoncée par la cible dans un champ qu'elle contrôle entièrement (ex : bannière `Server`, en-tête `X-Backend-Server`) — plausible mais falsifiable à volonté. |
| `CORROBORATED` | Une valeur `DECLARED` confirmée par un indice indépendant (ex : rôle SSH, le protocole ayant réellement été négocié). |
| `INFERRED` | Déduit d'un pattern/heuristique, sans déclaration explicite de la cible (ex : lien HTML). |
| `UNKNOWN` | Aucun indice exploitable, ou activement masqué par la cible. |

## 10. Protection contre les valeurs falsifiées

Omega-deep ne fait confiance à aucune donnée auto-déclarée par la cible sans le signaler explicitement — et la découverte de cibles est la partie la plus sensible du projet : une cible malveillante *pourrait* annoncer un `X-Backend-Server` mensonger pour orienter la découverte vers une IP de son choix. Deux protections structurelles, indépendantes l'une de l'autre :
- Aucune information dérivée d'une cible n'est jamais `VERIFIED` du simple fait d'être annoncée — une bannière `Server` ou un en-tête `X-Backend-Server` reste `DECLARED`, quelle que soit sa plausibilité.
- Le garde-fou de périmètre ([§4](#4-découverte-de-cibles-et-garde-fous)) borne où une cible annoncée peut mener (même `/24` privé, sauf configuration explicite), et la validation utilisateur borne si elle est scannée du tout — une cible mensongère hors périmètre n'est jamais même proposée ; une cible dans le périmètre reste soumise à confirmation explicite avant tout scan.

## 11. Compatibilité terminaux

Le TUI (Textual) détecte automatiquement les capacités du terminal (émulateur, taille) et adapte sa feuille de style structurelle en conséquence (`complete`/`standard`/`reduced`/`mono`), sans flag manuel. Le mode CLI reste toujours en texte simple, indépendant du terminal. Politique partagée par toute la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Profil selon l'émulateur détecté

| Émulateur | Profil initial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderne | `reduced` |
| TTY Linux, SSH legacy | `mono` |
| Émulateur non reconnu | `reduced` (repli par défaut) |

### Profil selon la taille du terminal

| Taille minimale (colonnes × lignes) | Plafond de profil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| en dessous | `mono` |

Le profil final retenu est **le plus restrictif des deux** (émulateur et taille) — un Ghostty en plein écran redimensionné à 70 colonnes redescend en `mono`, même si son émulateur autoriserait `complete`. Rafraîchissable en direct par la touche `r`.

## 12. Exports

Les rapports texte et HTML s'écrivent dans la langue choisie dans les Réglages (« Langue des exports », par défaut celle de l'interface) ; le JSON reste une donnée, non traduite. Les rapports sont générés dans `var/exports/` par défaut (chemin runtime ancré sur le dossier du projet, `$OMEGA_DEEP_VAR_DIR` pour le surcharger), ou au chemin indiqué (`--output` en CLI, boîte de dialogue en TUI). Nom de fichier explicite et horodaté : `analyse-{profil}-{date}.ext`, `analyse-custom-{date}.ext` pour un profil personnel.

### JSON, source de vérité

Structure complète de l'analyse (`Scan` + `Host[]` + `ArchitectureGraph`), strictement JSON-sérialisable, niveaux de confiance inclus.

### Texte, rapport humain compact

Lisible hors terminal, sans codes ANSI — graphe en liste d'arêtes.

### HTML, rapport web autonome

5 thèmes au choix (`--theme` en CLI, sélecteur en TUI ; suit le thème d'interface actif par défaut quand un équivalent existe). Mise en page dédiée : conteneur, grille d'infos, encarts de statistiques par état de port, badges colorés, **diagramme SVG du graphe d'architecture** (voir [§8](#8-graphe-darchitecture)) — même famille visuelle que `omega-scan`/`omega-check`.

## 13. Historique et comparaison

Chaque analyse est persistée (SQLite, `var/db/omega-deep.db`) : un `scan_id` porte la cible racine **et** tous les hosts découverts/acceptés, plus le graphe reconstruit. Historique consultable par cible racine (colonne dédiée au nombre de cibles découvertes), détail d'une analyse passée (hosts + graphe), comparaison entre deux analyses (état des ports de la **cible racine** uniquement — comparer les graphes de découverte serait une extension possible, non nécessaire à ce jour), et rejeu d'une analyse sur la même cible racine sans ressaisie.

## 14. Tests

```bash
source .venv/bin/activate
lint-imports        # verifie la Dependency Rule
pytest -q           # 191 tests
ruff check src tests
mypy -p omega_deep
```

Structure : `tests/unit/` (domaine et application, sans I/O réelle), `tests/integration/` (SQLite/fichiers réels, serveur HTTP factice `pytest-httpserver`, TLS via `trustme`), `tests/tui/` (navigation via `Pilot`, structurel — pas de vérification visuelle auto-revendiquée).

## 15. Hors périmètre

- Scan de CVE
- Détection active de SQLi, XSS, RCE
- Prise d'empreinte du système d'exploitation
- Techniques de scan bas niveau façon nmap (SYN scan, paquets bruts)
- Crawling
- Fuzzing
- Bruteforce
- Scan d'une cible découverte sans confirmation explicite — jamais, sous aucun mode
- Découverte hors du sous-réseau privé de la cible initiale sans configuration explicite
- Dashboard web

---

> Omega-deep — Découvrir, cartographier, qualifier, rapporter.
> Une architecture reconstruite avec une confiance explicite, jamais une supposition déguisée en fait.
