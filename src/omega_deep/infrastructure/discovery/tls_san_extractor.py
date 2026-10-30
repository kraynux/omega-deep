# Copyright (c) 2026 kraynux - Licence MIT
"""Extraction pure de candidats depuis les Subject Alternative Names d'un
certificat TLS deja collecte (voir infrastructure/network/ssl_tls_prober.py
::Service.tls_cert_san, format 'DNS:hostname'). Pas d'E/S — aucun nouveau
handshake TLS ici."""
from __future__ import annotations

from omega_deep.domain.targets.validation import normalize_target_input
from omega_deep.shared.i18n import _


def extract_from_tls_san(tls_cert_san: list[str]) -> list[tuple[str, str]]:
    """Une entree wildcard ('DNS:*.example.org') ne designe aucun host
    concret — ignoree."""
    results: list[tuple[str, str]] = []
    for entry in tls_cert_san:
        hostname = entry.removeprefix("DNS:").strip()
        if not hostname or "*" in hostname:
            continue
        candidate = normalize_target_input(hostname)
        if candidate:
            results.append((candidate, _("certificat SAN : {entry}").format(entry=entry)))
    return results
