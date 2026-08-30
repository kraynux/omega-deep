# Copyright (c) 2026 kraynux - Licence MIT
"""Regles de relation d'architecture (OMEGA-DEEP_SPECIFICATIONS.md §5.2).
Aucune E/S : mapping pur source de decouverte -> type de relation.

`backend_of` n'est volontairement PAS produit ici : ce serait l'arete
inverse d'un `proxy_to` (B backend_of A <=> A proxy_to B), un doublon
d'information plutot qu'une nouvelle deduction — a ajouter seulement s'il
sert un besoin de requetage reel (ex. "quels hosts sont des backends"),
pas par symetrie systematique. De meme, aucune detection de role "reverse
proxy" ici (domain/services/policies.py::infer_role documente deja ce
hors-perimetre) : les chaines de roles enrichies restent une extension
future, pas necessaires pour produire un graphe correct des relations
observees."""
from __future__ import annotations

_RELATION_BY_SOURCE: dict[str, str] = {
    "header": "proxy_to",  # A(NGINX) + en-tetes -> B(backend), voir spec §5.2
    "redirection": "redirect_to",
    "certificate": "linked_to",  # SAN partage : meme infrastructure/application
    "html_link": "linked_to",  # simple lien servi, relation la plus faible
}
_DEFAULT_RELATION = "linked_to"


def relation_type_for_source(discovery_source: str | None) -> str:
    """Source de decouverte (voir domain/discovery/models.py::DiscoveredTarget
    .source) -> type de relation d'architecture. Source inconnue/absente
    -> 'linked_to' (relation la plus neutre, jamais une supposition plus
    forte que les indices ne le justifient)."""
    if discovery_source is None:
        return _DEFAULT_RELATION
    return _RELATION_BY_SOURCE.get(discovery_source, _DEFAULT_RELATION)
