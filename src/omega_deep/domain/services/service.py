# Copyright (c) 2026 kraynux - Licence MIT
"""Orchestration pure du bounded context 'services' : fusion de plusieurs
resultats de sonde en un seul Service (mode HTTPS = HTTP + TLS combines).
Identique a omega-check."""
from __future__ import annotations

from dataclasses import replace

from omega_deep.domain.services.models import Service
from omega_deep.domain.services.policies import build_transport_layers, infer_role


def enrich_with_role_and_layers(port: int, strategy: str, service: Service) -> Service:
    """Applique les regles de role (policies.py::infer_role) et
    reconstruit la pile protocolaire (policies.py::build_transport_layers)
    sur un Service deja produit par une sonde. Appelee par
    application/commands/probe_service.py juste avant de retourner."""
    role, role_confidence = infer_role(port, service)
    return replace(
        service,
        role=role,
        role_confidence=role_confidence,
        encapsulation_layers=build_transport_layers(strategy),
    )


def merge_probes(*, http: Service | None, tls: Service | None) -> Service:
    """Combine un Service issu de HttpProber et un Service issu de
    TlsProber (voir ports/tls_prober.py) en un seul, pour un port HTTPS.
    Les champs tls_* viennent de `tls`, tout le reste de `http`. Si l'un
    des deux est absent, l'autre est retourne tel quel."""
    if http is None:
        return tls if tls is not None else Service()
    if tls is None:
        return http

    return Service(
        protocol_name=http.protocol_name,
        protocol_confidence=http.protocol_confidence,
        software=http.software,
        software_confidence=http.software_confidence,
        version=http.version,
        version_confidence=http.version_confidence,
        role=http.role,
        role_confidence=http.role_confidence,
        role_chain=list(http.role_chain),
        auth_required=http.auth_required,
        auth_required_confidence=http.auth_required_confidence,
        auth_types=list(http.auth_types),
        auth_types_confidence=http.auth_types_confidence,
        auth_details=dict(http.auth_details),
        firewall_app_present=http.firewall_app_present,
        firewall_app_confidence=http.firewall_app_confidence,
        waf_present=http.waf_present,
        waf_name_guess=http.waf_name_guess,
        waf_confidence=http.waf_confidence,
        tls_library=tls.tls_library,
        tls_library_confidence=tls.tls_library_confidence,
        tls_version=tls.tls_version,
        tls_version_confidence=tls.tls_version_confidence,
        tls_cipher=tls.tls_cipher,
        tls_cipher_confidence=tls.tls_cipher_confidence,
        tls_cert_subject=tls.tls_cert_subject,
        tls_cert_issuer=tls.tls_cert_issuer,
        tls_cert_san=list(tls.tls_cert_san),
        encapsulation_layers=list(http.encapsulation_layers),
        evidence=[*http.evidence, *tls.evidence],
    )
