# Architecture technique

Clean Architecture à 9 couches, identique dans son principe à `omega-scan`/`omega-check` (voir `~/DEV/SUITE/DECISIONS_ARCHITECTURE.md`, décisions D-000 et D-007 pour le rationnel du choix et la manière dont les contrats ont été portés).

## Dependency Rule

```
app                                     -- racine de composition
infrastructure | interfaces | plugins   -- adaptateurs, indépendants entre eux
application                             -- cas d'usage (commands/queries)
ports                                   -- contrats (Protocol)
domain                                  -- métier pur
core                                    -- vocabulaire transverse
```

Une couche ne peut importer que les couches strictement en dessous d'elle dans cette liste (l'extérieur dépend de l'intérieur, jamais l'inverse). Vérifié à chaque modification par `import-linter` (`lint-imports`), 6 contrats :

1. **Dependency Rule** (`type = "layers"`) : l'ordre ci-dessus.
2. **`interfaces` ne dépend jamais directement de `infrastructure`** : la CLI/TUI passe toujours par `application/`, jamais de raccourci vers un adaptateur concret.
3. **`httpx` confiné à `infrastructure.network`** — sondes de service ET de découverte (`infrastructure/discovery/http_discovery_prober.py` fait sa propre requête `httpx`, indépendante de `HttpxHttpProber`).
4. **`sqlite3` confiné à `infrastructure.storage.sqlite`**.
5. **`jinja2` confiné à `infrastructure.exporters.html_exporter`** — seul module autorisé à en importer ; le rendu SVG du graphe (`graph_layout.py`) ne l'importe volontairement pas (voir §Graphe plus bas).
6. **`textual` confiné à `interfaces.tui`** (avec une exception explicite pour `interfaces.cli`, qui doit aussi rester indépendant de `textual`) — actif, la TUI est construite (contrairement au TUI de CHECK au moment où son propre `ARCHITECTURE.md` a été écrit : ce contrat n'était alors pas encore utile).

## Pourquoi `Protocol` et pas `ABC`

Tous les ports (`ports/*.py`) sont des `typing.Protocol`, pas des `abc.ABC`. Les implémentations ne héritent pas explicitement du port — typage structurel, juste une docstring notant quel port est implémenté (ex. `"""Implemente ports/discovery_prober.py::DiscoveryProber."""`).

## Bounded contexts de `domain/`

| Sous-package | Contenu | Remarque |
|---|---|---|
| `domain/scans/` | `Scan`, cycle de vie d'une analyse | Étendu vs. omega-check : `analysis_mode`, `root_target_ip`, `discovered_targets`, garde-fous (`max_depth`, `max_additional_targets`, `allowed_subnet`). |
| `domain/targets/` | `Host` | Étendu vs. omega-check : provenance de découverte (`depth_level`, `discovered_from`, `discovery_source`, `discovery_confidence`). |
| `domain/services/` | `Port`, `Service`, `RoleElement`, `TransportLayer`, règles (`policies.py`), fusion de sondes (`service.py`) | **Identique** à omega-check (D-005). |
| `domain/profiles/` | `Profile`, profils système, règles de validation | **Identique** à omega-check. |
| `domain/reports/` | Comparaison de deux analyses (hosts racine uniquement) | **Identique** à omega-check dans son principe — voir limites plus bas. |
| `domain/discovery/` | `DiscoveredTarget`, machine à états `DiscoveryState` (D-003), garde-fous purs (`policies.py::is_within_allowed_scope`/`is_depth_allowed`/`is_additional_target_count_allowed`) | **Nouveau pour DEEP** — aucune E/S, testable sans réseau. |
| `domain/architecture/` | `ArchitectureGraph`, `ArchitectureEdge`, reconstruction (`service.py::reconstruct_architecture`), règles de relation (`policies.py::relation_type_for_source`) | **Nouveau pour DEEP** — reconstruit uniquement depuis la provenance déjà portée par chaque `Host`, aucune E/S. |

## Les deux pipelines

### Scan fixe (brique disponible, pas exposée par une interface)

```
application/commands/run_scan.py
  ├─ ports/dns_resolver.py                → résolution de la cible
  └─ application/commands/scan_host.py    → scan de ports + identification de service (voir ci-dessous)
       └─ ports/scan_repository.py::save() + save_hosts([host])   → persistance SQLite
```

`run_scan()` reste utile tel quel pour un scan à cible unique sans découverte — mais aucune sous-commande CLI ni écran TUI ne l'appelle actuellement (`analyze` est la seule voie d'entrée). Conservé comme brique testée et documentée, pas du code mort par oubli : une éventuelle sous-commande `scan` (mode `FIXED`, symétrique à omega-check) pourrait s'y brancher directement le jour où le besoin est confirmé.

### Analyse multi-cibles (le pipeline réellement exposé)

```
interfaces/cli/commands/analyze_command.py (CLI)  /  screens/scan_progress.py (TUI)
  ├─ application/commands/scan_host.py                         → scan de la cible racine (depth_level=0)
  │    ├─ ports/port_prober.py (par port)                       → open/closed/filtered
  │    └─ pour chaque port OPEN : application/commands/probe_service.py
  │         ├─ domain/services/policies.py::classify_probe_strategy(port)
  │         ├─ ports/http_prober.py + ports/tls_prober.py (HTTPS)
  │         └─ ports/ssh_prober.py / ports/vnc_prober.py / ports/generic_banner_prober.py
  ├─ boucle BFS, pour chaque host tant que profondeur < max_depth :
  │    ├─ application/commands/discover_targets.py
  │    │    ├─ ports/discovery_prober.py (en-têtes, redirection, certificat, liens HTML)
  │    │    └─ domain/discovery/service.py::filter_discovered_targets (garde-fous de périmètre/nombre)
  │    ├─ validation utilisateur (CLI : question par cible ; TUI : screens/target_validation.py)
  │    ├─ application/commands/validate_targets.py               → PROPOSED → ACCEPTED/REJECTED (fail-safe)
  │    └─ pour chaque cible ACCEPTED : scan_host.py à nouveau (depth_level+1, provenance renseignée)
  ├─ domain/architecture/service.py::reconstruct_architecture(hosts)
  └─ ports/scan_repository.py::save() + save_hosts(tous les hosts) + save_graph()   → UN SEUL scan_id
```

Le point clé : c'est `analyze_command.py` (CLI) et `screens/scan_progress.py::AnalyzeProgressScreen` (TUI) qui orchestrent cette boucle, pas un use case `application/` pur — `validate_targets` exige une confirmation humaine par cible (D-003), une opération qui ne peut pas vivre dans une fonction non-interactive de la couche application. Côté TUI, l'écran de validation est poussé via `app.push_screen_wait(...)`, ce qui suspend le worker d'analyse (lui-même asynchrone, chaque appel bloquant passant par `asyncio.to_thread`) le temps de la décision.

## Graphe d'architecture

`domain/architecture/service.py::reconstruct_architecture(hosts)` ne relit que la provenance déjà portée par chaque `Host` (`discovered_from`/`discovery_source`/`discovery_confidence`) — aucune E/S, aucun re-parcours des indices bruts. `domain/architecture/policies.py::relation_type_for_source` mappe la source de découverte vers un type de relation (`header` → `proxy_to`, `redirection` → `redirect_to`, `certificate`/`html_link` → `linked_to`) ; `backend_of` (l'arête inverse d'un `proxy_to`) est volontairement jamais produit — ce serait un doublon d'information, pas une nouvelle déduction.

Le rendu diffère selon l'interface :
- TUI et exports JSON/texte : liste des arêtes — un terminal ou un format texte n'a pas besoin d'un rendu graphique riche.
- Export HTML : `infrastructure/exporters/graph_layout.py::render_architecture_svg(graph, palette)` — mise en page en couches par BFS depuis `graph.root_node`, calculée en Python pur (pas de dépendance de layout de graphe lourde type `graphviz`, le graphe reste petit par construction). N'importe **pas** `jinja2` (seul `html_exporter.py` y est autorisé, voir contrat import-linter) : construit une chaîne `<svg>...</svg>` autonome, insérée par le template via `| safe`. Toutes les valeurs dynamiques (IP, type de relation) sont échappées (`xml.sax.saxutils.escape`) avant insertion — elles proviennent in fine d'un en-tête ou d'un lien HTML d'une cible scannée, jamais dignes de confiance par défaut.

## Limites connues (documentées, pas des oublis)

- **Détection de reverse proxy / cache HTTP pour le RÔLE d'un host** : `domain/services/policies.py` (identique à omega-check) ne déduit toujours pas qu'un host EST un reverse proxy à partir de ses propres en-têtes de réponse. Ne pas confondre avec la découverte (`domain/discovery/`), qui utilise des en-têtes voisins (`X-Forwarded-Host`, etc.) mais dans un but différent : proposer une NOUVELLE cible, pas qualifier le rôle de l'hôte qui les émet.
- **Chaînes de rôles inter-ports sur un même host** (ex. NGINX:80 → Lighttpd:8080) : dépend de la même détection manquante ci-dessus. Le graphe d'architecture, lui, relie des HOSTS entre eux (pas des ports d'un même host).
- **Authentification SSH** : seul le banner est lu. L'énumération des méthodes d'authentification demanderait un échange de clés SSH partiel, hors-scope.
- **VNC** : la sonde s'arrête après la négociation des security types, avant toute tentative d'authentification.
- **Découverte HTML** : un seul niveau — les liens de la page de la cible RACINE d'un host sont extraits, pas un crawl récursif au sein même de ce host. La profondeur (`--max-depth`) parcourt des HOSTS différents, pas des pages d'un même host.
- **Comparaison de deux analyses** : compare seulement les hosts RACINE des deux analyses (`domain/reports/comparison.py`, identique dans son principe à omega-check) — comparer les graphes de cibles découvertes entre deux analyses serait une extension possible, non demandée à ce jour, pour éviter la sur-ingénierie.

## Bibliothèque partagée (`omega-lib`)

`ConfidenceLevel`, les utilitaires transverses (`clock`, `ids`, `typing`), le système de thème (`theme/{models,policies,service}.py` — 10 thèmes TUI + 5 thèmes d'export) et la détection terminal (`terminal/*`, `infrastructure/terminal/*`, ports `terminal_detector`/`settings_store`) viennent de `~/DEV/LIB/omega-lib` (vendorisé dans `vendor/omega-lib/` pour l'installation packagée, voir D-005/D-008) — identique à omega-check, aucune divergence.

Le reste (probes de service, modèles `Scan`/`Host`/`Port`/`Service`) reste dupliqué entre `omega-check` et `omega-deep`, décision assumée (D-005) pour éviter la sur-généralisation avant d'avoir plusieurs implémentations réelles à comparer. `domain/discovery/` et `domain/architecture/` sont propres à DEEP, pas mutualisés (pas de besoin identifié chez `omega-check`, qui n'a pas de concept de cible découverte).

## Interface TUI

`interfaces/tui/` suit le même patron que `omega-check` (lui-même aligné sur `omega-scan`/`omega-stress`) : `app.py` (résout thème + profil de rendu au démarrage, enchaîne splash → accueil), `screens/_base.py::OmegaScreen` (retour `Échap` uniforme), `controllers/startup_controller.py`, `rendering/{stylesheet_loader,textual_theme_builder}.py`. Les feuilles de style (`styles/{base,complete,standard,reduced,mono}.tcss`) et les conventions visuelles (`.omega-btn-frame`/`.omega-actions`/etc.) sont portées verbatim.

Différences assumées avec omega-check :
- Pas d'écran "Cibles" (pas de concept de cible épinglée chez DEEP).
- Gestion des profils personnels (`ProfilesScreen`) construite dès la première version, pas ajoutée après coup (contrairement à CHECK).
- Un écran sans équivalent chez aucun autre outil de la suite : `screens/target_validation.py`, la validation interactive des cibles découvertes — remplace, côté TUI, les prompts `input()` du CLI.
- Splash plus dense/technique (composition intégrée icône-ordinateur + serveur + hub réseau, pas une pile de blocs indépendants) — voir `~/DEV/DEEP/ascii.txt` pour le contenu source et son guide de couleurs.

Le TUI de DEEP a été ajouté après coup dans le calendrier de développement (CHECK et DEEP devaient à l'origine être un seul outil, scindés plus tard — voir `~/DEV/SUITE/DECISIONS_ARCHITECTURE.md` D-009) : ce n'était pas un choix délibéré de retarder le TUI, un oubli de la scission corrigé depuis.
