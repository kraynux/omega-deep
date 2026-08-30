# Analyse d'architecture multi-cibles

Ce document explique le fonctionnement de la fonctionnalité qui distingue omega-deep d'omega-check : la découverte de cibles au-delà de celle demandée, et la reconstruction d'un graphe d'architecture à partir de ce qui a été trouvé. Pour le détail technique (couches, pipeline interne), voir `docs/ARCHITECTURE.md` — ce document-ci se lit du point de vue de l'utilisateur.

## Le problème que ça résout

Scanner une IP donne une photo d'un seul point. Or beaucoup d'infrastructures sont composées de plusieurs machines qui se parlent entre elles : un reverse-proxy devant deux backends, un serveur qui redirige vers un autre nom, un certificat qui couvre plusieurs hôtes. Omega-check répond à *"qu'est-ce qui tourne sur cette IP ?"* ; omega-deep répond en plus à *"et derrière, qu'est-ce qu'il y a d'autre ?"* — sans jamais scanner quoi que ce soit sans confirmation.

## Comment une cible est proposée

Après avoir scanné un host, omega-deep relit les indices qu'il a déjà collectés au passage (aucune requête supplémentaire dédiée à la découverte) et en extrait des cibles candidates :

| Indice observé | Source | Exemple concret |
|---|---|---|
| En-tête de réponse HTTP | `header` | `X-Backend-Server: 10.0.0.5:8080`, `X-Forwarded-Host: app.interne.lan`, `Via: 1.1 proxy.interne` |
| Redirection HTTP | `redirection` | Réponse `301` avec `Location: https://10.0.0.6/` |
| Certificat TLS négocié | `certificate` | SAN du certificat listant `backend.interne.lan` en plus du nom demandé |
| Lien dans la page | `html_link` | `<a href="http://10.0.0.7:8000/admin">` dans le corps HTML retourné |

Chaque candidat passe par un filtre de périmètre **avant** d'être proposé (voir plus bas) — une cible hors périmètre n'apparaît jamais à l'écran de validation, elle n'est même pas comptée dans le nombre de cibles découvertes.

## Les relations du graphe

Une fois une cible découverte acceptée et scannée, la relation avec le host qui l'a révélée est enregistrée avec un type :

- **`proxy_to`** (indice : en-tête) — le host source semble être un proxy vers la cible découverte. C'est la lecture la plus courante d'un `X-Backend-Server` ou `X-Forwarded-Host`.
- **`redirect_to`** (indice : redirection) — une redirection HTTP a été observée vers la cible découverte.
- **`linked_to`** (indice : certificat ou lien HTML) — relation la plus neutre : les deux hosts partagent probablement une infrastructure ou une application, sans qu'un sens de flux soit affirmé.

Il n'y a volontairement **pas** de relation `backend_of` : ce serait l'arête inverse d'un `proxy_to` (B backend_of A ⟺ A proxy_to B), une duplication d'information plutôt qu'une nouvelle déduction.

### Ce qu'une relation affirme réellement

Chaque relation porte une confiance ([§9 du README](../README.md#9-politique-de-confiance)) — presque toujours `DECLARED` (le host source l'a annoncé lui-même, dans un champ qu'il contrôle entièrement) ou `INFERRED` (déduit d'un simple lien, sans déclaration). **Jamais `VERIFIED`** : rien ne prouve indépendamment qu'un `X-Backend-Server` correspond à une relation réelle plutôt qu'à une valeur choisie par l'administrateur (ou falsifiée par un attaquant, voir [§10 du README](../README.md#10-protection-contre-les-valeurs-falsifiées)). Une relation `proxy_to [declared]` doit se lire comme *"127.0.0.1 déclare que 127.0.0.2 est son backend"*, pas comme *"127.0.0.1 EST prouvé être un proxy vers 127.0.0.2"`.

## Lire le diagramme

Dans l'export HTML, chaque nœud est un cercle — plein (couleur d'accent) pour la cible racine, en contour pour les cibles découvertes — étiqueté par son IP. Les cibles sont disposées par couches selon leur profondeur de découverte (la racine en haut, ses découvertes directes juste en dessous, etc.). Chaque flèche porte le type de relation et la confiance associée. Dans le TUI et les exports texte/JSON, la même information est disponible sous forme de liste d'arêtes (`source -[relation, confiance]-> cible`) — pas de rendu graphique riche dans un terminal.

## Régler les garde-fous selon le contexte

Les trois garde-fous (`--max-depth`, `--max-targets`, `--subnet`) ne sont **jamais désactivables**, seulement ajustables :

- **Petit LAN domestique/labo** : les valeurs par défaut (profondeur 3, 10 cibles) suffisent largement — une box, deux ou trois serveurs, une caméra IP ne dépassent pas ces bornes.
- **Segment plus grand ou datacenter** : augmenter `--max-targets` a du sens si beaucoup de backends légitimes sont attendus derrière un même load-balancer ; augmenter `--max-depth` a plus rarement du sens (au-delà de 3 sauts, la confiance de la chaîne se dilue déjà beaucoup).
- **Découverte volontairement désactivée** : `--max-depth 1` — seule la cible racine est scannée, aucune découverte n'est même tentée (utile pour un scan "comme omega-check", ou pour vérifier qu'aucune cible ne se propose avant d'élargir).
- **Sous-réseau hors du `/24` privé de la racine** (y compris des IPs publiques) : uniquement via `--subnet` explicite — c'est la configuration explicite qui autorise l'exception, jamais un comportement par défaut.

## Ce que le graphe ne dit pas

- **Pas de garantie d'exhaustivité** : seuls les indices que la sonde sait extraire (§ ci-dessus) sont suivis. Un backend référencé autrement (fichier de config non exposé, DNS interne non résolu depuis la machine qui scanne) n'apparaîtra jamais.
- **Découverte HTML limitée à une page** : les liens de la page racine d'un host sont extraits, pas un crawl récursif au sein de ce même host — la profondeur parcourt des HOSTS différents, pas des pages.
- **La comparaison entre deux analyses ne porte que sur la cible racine** (état de ses ports) — comparer les graphes de découverte de deux analyses dans le temps n'est pas implémenté à ce jour.
- **Un même graphe peut varier d'une analyse à l'autre** sans que rien n'ait changé côté infrastructure : l'ordre de découverte (BFS) et les limites de garde-fous peuvent faire qu'une cible acceptée lors d'une analyse n'est même pas proposée lors d'une autre (nombre de cibles déjà atteint avant de l'atteindre, par exemple).
