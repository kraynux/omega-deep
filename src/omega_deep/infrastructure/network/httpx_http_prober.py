# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation httpx du port HttpProber. Collecte brute + delegation de
l'interpretation a domain/services/policies.py (garde les regles testables
sans mock reseau). Identique a omega-check, y compris son correctif SNI :

sur une cible avec hebergement virtuel base sur le SNI (Cloudflare et la
plupart des CDN/reverse proxies), se connecter directement a `target_ip`
sans extension `sni_hostname` fait presenter l'IP (ou rien) comme nom SNI
au serveur, qui rejette la poignee de main faute de pouvoir choisir le bon
certificat/virtual host. Fix : extension `sni_hostname=host_header`
(supportee par httpx/httpcore) — la connexion TCP reste sur `target_ip`
(pas de nouvelle resolution DNS), seul le SNI presente change."""
from __future__ import annotations

import httpx

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.services.models import Service
from omega_deep.domain.services.policies import classify_http_auth, detect_waf, parse_server_header

USER_AGENT = "omega-deep-httpx/1.0"
"""Identifie le trafic genere dans les journaux de la cible plutot que de
laisser l'en-tete par defaut de httpx (python-httpx/x.y.z) — meme
raisonnement que omega-check/omega-stress."""


class HttpxHttpProber:
    """Implemente ports/http_prober.py::HttpProber."""

    def probe(
        self, target_ip: str, port: int, host_header: str, timeout: float, use_tls: bool
    ) -> Service:
        scheme = "https" if use_tls else "http"
        url = f"{scheme}://{target_ip}:{port}/"

        extensions = {"sni_hostname": host_header} if use_tls else {}
        request_headers = {"Host": host_header, "User-Agent": USER_AGENT}
        try:
            with httpx.Client(timeout=timeout, follow_redirects=False, verify=False) as client:
                response = client.get(url, headers=request_headers, extensions=extensions)
        except httpx.HTTPError as exc:
            return Service(
                protocol_confidence=ConfidenceLevel.UNKNOWN,
                evidence=[f"echec de la requete HTTP : {exc}"],
            )

        headers = dict(response.headers)
        software, version = parse_server_header(headers.get("server"))
        auth_required, auth_confidence, auth_types, auth_types_confidence = classify_http_auth(
            response.status_code, headers
        )
        waf_present, waf_name, waf_confidence = detect_waf(headers)

        evidence = [f"HTTP {response.status_code} {response.reason_phrase}"]
        if "server" in headers:
            evidence.append(f"header Server: {headers['server']}")

        return Service(
            protocol_name="HTTPS" if use_tls else "HTTP",
            protocol_confidence=ConfidenceLevel.VERIFIED,
            software=software,
            software_confidence=ConfidenceLevel.DECLARED if software else ConfidenceLevel.UNKNOWN,
            version=version,
            version_confidence=ConfidenceLevel.DECLARED if version else ConfidenceLevel.UNKNOWN,
            auth_required=auth_required,
            auth_required_confidence=auth_confidence,
            auth_types=auth_types,
            auth_types_confidence=auth_types_confidence,
            waf_present=waf_present,
            waf_name_guess=waf_name,
            waf_confidence=waf_confidence,
            evidence=evidence,
        )
