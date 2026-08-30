# Copyright (c) 2026 kraynux - Licence MIT
"""Extraction pure de candidats depuis l'en-tete de redirection HTTP
(Location — voir OMEGA-DEEP_SPECIFICATIONS.md §4.2). Pas d'E/S."""
from __future__ import annotations

from omega_deep.domain.targets.validation import normalize_target_input


def extract_from_redirect(location: str | None) -> list[tuple[str, str]]:
    """Un chemin relatif ('/login') ne revele aucun nouvel hote — ignore.
    Seule une URL absolue (http(s)://...) est une decouverte."""
    if not location:
        return []
    if not location.lower().startswith(("http://", "https://")):
        return []

    candidate = normalize_target_input(location)
    if not candidate:
        return []
    return [(candidate, f"redirection Location: {location}")]
