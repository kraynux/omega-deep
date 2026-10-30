# Copyright (c) 2026 kraynux - Licence MIT
"""Extraction pure de candidats depuis les liens absolus d'une page HTML
(href/src — voir OMEGA-DEEP_SPECIFICATIONS.md §4.2). Regex volontairement
simple (pas de dependance HTML-parser supplementaire, voir
~/DEV/SUITE/DECISIONS_ARCHITECTURE.md D-002 : extraction HTML dupliquee
avec omega-fold pour l'instant, pas encore mutualisee) : seuls les liens
ABSOLUS (http(s)://...) revelent un autre hote, les liens relatifs
('/style.css') restent sur le meme host et sont ignores."""
from __future__ import annotations

import re

from omega_deep.domain.targets.validation import normalize_target_input
from omega_deep.shared.i18n import _

_ABSOLUTE_LINK_RE = re.compile(r'(?:href|src)\s*=\s*["\']?(https?://[^"\'\s>]+)', re.IGNORECASE)


def extract_from_html_links(html_body: str | None) -> list[tuple[str, str]]:
    if not html_body:
        return []

    results: list[tuple[str, str]] = []
    for match in _ABSOLUTE_LINK_RE.finditer(html_body):
        url = match.group(1)
        candidate = normalize_target_input(url)
        if candidate:
            results.append((candidate, _("lien HTML : {url}").format(url=url)))
    return results
