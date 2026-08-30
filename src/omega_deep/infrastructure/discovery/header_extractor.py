# Copyright (c) 2026 kraynux - Licence MIT
"""Extraction pure de candidats depuis les en-tetes HTTP de decouverte
(X-Forwarded-Host, X-Real-IP, X-Backend-Server, Via — voir
OMEGA-DEEP_SPECIFICATIONS.md §4.2). Pas d'E/S : opere sur un dict de
headers deja collecte."""
from __future__ import annotations

from omega_deep.domain.targets.validation import normalize_target_input

_DISCOVERY_HEADERS = ("x-forwarded-host", "x-real-ip", "x-backend-server", "via")


def extract_from_headers(headers: dict[str, str]) -> list[tuple[str, str]]:
    """Retourne [(candidat_normalise, detail_evidence), ...]. `Via` a un
    format different (RFC 7230 §5.7.1 : '1.1 proxy.example.com') — on
    prend le dernier token separe par un espace de chaque segment separe
    par une virgule, ce qui gere aussi le cas simple d'un header a valeur
    unique sans espace (le token est alors la valeur entiere)."""
    results: list[tuple[str, str]] = []
    lower_headers = {k.lower(): v for k, v in headers.items()}

    for header_name in _DISCOVERY_HEADERS:
        value = lower_headers.get(header_name)
        if not value:
            continue
        for segment in value.split(","):
            segment = segment.strip()
            if not segment:
                continue
            token = segment.split()[-1]
            candidate = normalize_target_input(token)
            if candidate:
                results.append((candidate, f"header {header_name}: {segment}"))

    return results
