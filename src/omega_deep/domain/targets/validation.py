# Copyright (c) 2026 kraynux - Licence MIT
"""Normalisation d'une saisie de cible (bounded context 'targets').
Identique a omega-check — retire schema ('http://'/'https://')/port/chemin
avant resolution DNS de la cible initiale (pas des cibles decouvertes,
voir domain/discovery/ pour celles-ci, phase ulterieure)."""
from __future__ import annotations

_SCHEMES = ("https://", "http://")


def normalize_target_input(raw: str) -> str:
    """'http://exemple.org:8080/chemin' -> 'exemple.org'. Idempotent sur une
    cible deja propre (IP ou hostname nu)."""
    target = raw.strip()

    for scheme in _SCHEMES:
        if target.lower().startswith(scheme):
            target = target[len(scheme) :]
            break

    target = target.split("/", 1)[0]

    if target.count(":") == 1:
        host, _, port = target.partition(":")
        if port.isdigit():
            target = host

    return target
