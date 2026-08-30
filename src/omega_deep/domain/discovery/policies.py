# Copyright (c) 2026 kraynux - Licence MIT
"""Garde-fous de la decouverte de cibles (OMEGA-DEEP_SPECIFICATIONS.md
§4.2) — le coeur de la securite d'OMEGA-DEEP (voir
OMEGA-DEEP_ARBORESCENCE.md §4). Aucune E/S ici : pure logique de filtrage
sur des chaines/adresses deja extraites, testable sans reseau.

Regle fail-safe deliberee : un candidat qui n'est pas un litteral IP
valide (ex. un hostname non resolu extrait d'un header/lien HTML) est
REJETE par `is_within_allowed_scope`, jamais accepte par defaut — verifier
le perimetre d'un hostname demanderait de le resoudre, une etape reseau
hors de ce module pur ; en son absence, l'option sure est de ne pas le
proposer plutot que de supposer qu'il est dans le perimetre."""
from __future__ import annotations

import ipaddress

_DEFAULT_PREFIX_LENGTH = 24
"""Taille de subnet implicite (LAN /24) quand `allowed_subnet` n'est pas
fourni explicitement — heuristique raisonnable pour un usage IPv4/LAN,
pas une detection de topologie reelle. Voir --subnet (CLI, phase
ulterieure) pour un controle explicite."""


def is_within_allowed_scope(candidate: str, root_ip: str, allowed_subnet: str | None = None) -> bool:
    """True si `candidate` peut etre propose comme cible decouverte.

    - `allowed_subnet` fourni explicitement (ex. "192.168.1.0/24") :
      seule condition, y compris si le subnet couvre des IPs publiques —
      c'est la "configuration explicite" qui autorise cette exception
      (voir OMEGA-DEEP_SPECIFICATIONS.md §4.2).
    - Sinon : `candidate` doit etre une IP privee (jamais publique par
      defaut) ET dans le meme /24 que `root_ip`.
    - `candidate`/`root_ip` non parsable en IP (hostname, chaine invalide) :
      False (voir note fail-safe en tete de module).
    """
    try:
        candidate_ip = ipaddress.ip_address(candidate)
    except ValueError:
        return False

    if allowed_subnet is not None:
        network = ipaddress.ip_network(allowed_subnet, strict=False)
        return candidate_ip in network

    if not candidate_ip.is_private:
        return False

    try:
        root = ipaddress.ip_address(root_ip)
    except ValueError:
        return False

    root_network = ipaddress.ip_network(f"{root}/{_DEFAULT_PREFIX_LENGTH}", strict=False)
    return candidate_ip in root_network


def is_depth_allowed(current_depth: int, max_depth: int) -> bool:
    """True si une decouverte au niveau `current_depth + 1` reste autorisee
    (OMEGA-DEEP_SPECIFICATIONS.md §1.2 : max 3 sauts par defaut, A -> B ->
    C -> D max — `max_depth=3` autorise depth_level jusqu'a 3 inclus)."""
    return current_depth < max_depth


def is_additional_target_count_allowed(current_count: int, max_additional_targets: int) -> bool:
    """True si une cible decouverte de plus reste autorisee (nombre de
    cibles deja acceptees/proposees < maximum)."""
    return current_count < max_additional_targets
