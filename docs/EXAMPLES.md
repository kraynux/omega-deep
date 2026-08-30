# Exemples d'usage

## Analyser une cible (avec découverte)

```bash
$ omega-deep analyze 127.0.0.1 --profile web
2026-08-31 00:40:26 INFO omega_deep.scan: Scan du port 8080/tcp...
2026-08-31 00:40:26 INFO omega_deep.scan: Port 8080/tcp : open
2026-08-31 00:40:26 INFO omega_deep.scan: Identification du service sur le port 8080...
[...]
2026-08-31 00:40:27 INFO omega_deep.scan: Host 127.0.0.1 : 16 port(s) analyse(s).

1 cible(s) decouverte(s) depuis 127.0.0.1 :
  127.0.0.2 — source: header, confiance: declared
    header x-backend-server: 127.0.0.2:8000
  Scanner 127.0.0.2 ? [o/N] o
2026-08-31 00:40:27 INFO omega_deep.scan: Scan du port 8000/tcp...
2026-08-31 00:40:27 INFO omega_deep.scan: Port 8000/tcp : open
[...]
2026-08-31 00:40:27 INFO omega_deep.scan: Host 127.0.0.2 : 16 port(s) analyse(s).
Scan 38747f66bd294bbfa677351b73f0bf07 — cible 127.0.0.1 (127.0.0.1) — mode deep — statut completed
[cible initiale] 127.0.0.1 — 16 port(s) scanne(s) :
   8080/tcp — open     [verified]
         └─ HTTP BaseHTTP 0.6, role=serveur web [inferred]
    [... 15 autres ports, tous closed ...]
[cible decouverte (profondeur 1)] 127.0.0.2 — 16 port(s) scanne(s) :
   8000/tcp — open     [verified]
         └─ HTTP BaseHTTP 0.6, role=serveur web [inferred]
    [... 15 autres ports, tous closed ...]
Graphe d'architecture :
  127.0.0.1 --proxy_to--> 127.0.0.2 [declared]
```

Ce que fait `127.0.0.1` ici : il répond avec l'en-tête `X-Backend-Server: 127.0.0.2:8000`, exactement comme le ferait un reverse-proxy annonçant son backend. Omega-deep propose `127.0.0.2` — jamais ne le scanne tant que la question n'a pas reçu de réponse explicite. Répondre autre chose que `o`/`oui`/`y`/`yes` (ou fermer le terminal, ou lancer sans TTY) rejette la cible : le silence n'est jamais une acceptation.

Reproductible en local sans lab autorisé ni adresse publique — `scripts/local_test_lab.py` démarre deux serveurs HTTP loopback (`127.0.0.1`/`127.0.0.2`, toujours autorisés à scanner sur sa propre machine) reproduisant exactement ce scénario :

```bash
python3 scripts/local_test_lab.py   # terminal 1, laisser tourner
omega-deep analyze 127.0.0.1 --profile web   # terminal 2
```

## Consulter l'historique

```bash
$ omega-deep history --limit 5
38747f66bd294bbfa677351b73f0bf07  2026-08-30T22:40:26+00:00  127.0.0.1 (127.0.0.1)  mode=deep  completed
```

## Exporter un rapport

```bash
# Texte détaillé sur stdout
omega-deep show 38747f66bd294bbfa677351b73f0bf07

# JSON complet (structure de l'agrégat Scan + Host[] + ArchitectureGraph)
omega-deep show 38747f66bd294bbfa677351b73f0bf07 --format json

# HTML avec diagramme du graphe, écrit dans un fichier
omega-deep show 38747f66bd294bbfa677351b73f0bf07 --format html --theme omega-neon --output rapport.html
```

## Comparer deux analyses dans le temps

```bash
$ omega-deep analyze 192.168.1.10 --profile web   # analyse initiale
$ omega-deep analyze 192.168.1.10 --profile web   # quelques jours plus tard
$ omega-deep compare <scan_id_ancien> <scan_id_recent>
Comparaison <scan_id_ancien> -> <scan_id_recent>
Ports presents seulement dans <scan_id_recent> : [8443]
Changements d'etat :
  port 8080 : closed -> open
```

Compare uniquement les **cibles racine** des deux analyses — utile pour repérer une dérive sur l'hôte que vous surveillez, pas sur ce qui a pu être découvert autour.

## Créer un profil de ports sur mesure

```bash
$ omega-deep profile create labo --ports 22,8080,8443 --description "Bastion + app interne"
Profil 'labo' cree (3 port(s)).

$ omega-deep analyze 10.0.0.5 --profile labo --max-depth 2 --max-targets 5
```

## Restreindre ou élargir la découverte

```bash
# Découverte désactivée de fait : profondeur 1 = seule la racine est scannée
omega-deep analyze target.example --profile minimal --max-depth 1

# Sous-réseau explicite (nécessaire pour autoriser une découverte hors du /24
# privé de la racine, y compris vers des IPs publiques si le sous-réseau
# donné en couvre — la configuration explicite est ce qui autorise l'exception)
omega-deep analyze target.example --profile web --subnet 10.0.0.0/16

# Nombre de cibles supplémentaires borné à 3, quelle que soit la profondeur atteinte
omega-deep analyze target.example --profile web --max-targets 3
```

## Workflow typique (cartographie d'une infrastructure interne)

```bash
# 1. Analyse initiale de référence (noter le scan_id affiché), garde-fous par
#    defaut (profondeur 3, 10 cibles max, meme /24 prive que la racine)
omega-deep analyze gateway.lan --profile web

# 2. Revue du graphe reconstruit
omega-deep show <scan_id> --format html --output architecture.html

# 3. Analyses régulières (cron, etc.) pour détecter une dérive de topologie
omega-deep analyze gateway.lan --profile web
omega-deep history --target gateway.lan

# 4. Comparaison avec la référence (cible racine uniquement)
omega-deep compare <id_baseline> <id_dernier>
```
