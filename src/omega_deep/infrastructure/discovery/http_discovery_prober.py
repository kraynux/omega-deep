# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation httpx du port DiscoveryProber (ports/discovery_prober.py).

Fait sa propre requete HTTP legere (headers + corps HTML, tronque a
_MAX_HTML_BODY_CHARS par prudence) — independante de HttpxHttpProber
(infrastructure/network/), qui ne conserve pas les en-tetes bruts
necessaires ici. Le SAN du certificat n'est PAS recollecte (deja fourni
en parametre par l'appelant, depuis TlsProber). Aucun filtrage de
perimetre ici : voir domain/discovery/service.py::filter_discovered_targets,
applique separement par l'appelant (application/commands/discover_targets.py,
phase ulterieure)."""
from __future__ import annotations

import httpx

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.discovery.models import DiscoveredTarget
from omega_deep.infrastructure.discovery.header_extractor import extract_from_headers
from omega_deep.infrastructure.discovery.html_link_extractor import extract_from_html_links
from omega_deep.infrastructure.discovery.redirect_extractor import extract_from_redirect
from omega_deep.infrastructure.discovery.tls_san_extractor import extract_from_tls_san

USER_AGENT = "omega-deep-httpx/1.0"
_MAX_HTML_BODY_CHARS = 200_000

_CONFIDENCE_BY_SOURCE: dict[str, ConfidenceLevel] = {
    "certificate": ConfidenceLevel.DECLARED,
    "header": ConfidenceLevel.DECLARED,
    "redirection": ConfidenceLevel.DECLARED,
    "html_link": ConfidenceLevel.INFERRED,
}
"""header/redirection/certificate : la cible (ou son certificat) declare
elle-meme cette information — falsifiable, jamais VERIFIED (D-001).
html_link : simple lien servi par la page, aucune declaration explicite
de relation d'infrastructure — INFERRED, plus faible."""


class HttpDiscoveryProber:
    """Implemente ports/discovery_prober.py::DiscoveryProber."""

    def probe(
        self,
        target_ip: str,
        port: int,
        host_header: str,
        timeout: float,
        use_tls: bool,
        tls_cert_san: list[str],
    ) -> list[DiscoveredTarget]:
        candidates: list[DiscoveredTarget] = []
        candidates.extend(
            self._to_targets(extract_from_tls_san(tls_cert_san), "certificate", target_ip)
        )

        scheme = "https" if use_tls else "http"
        url = f"{scheme}://{target_ip}:{port}/"
        extensions = {"sni_hostname": host_header} if use_tls else {}
        request_headers = {"Host": host_header, "User-Agent": USER_AGENT}

        try:
            with httpx.Client(timeout=timeout, follow_redirects=False, verify=False) as client:
                response = client.get(url, headers=request_headers, extensions=extensions)
        except httpx.HTTPError:
            return candidates  # au moins le certificat, si disponible

        headers = dict(response.headers)
        candidates.extend(self._to_targets(extract_from_headers(headers), "header", target_ip))
        candidates.extend(
            self._to_targets(extract_from_redirect(headers.get("location")), "redirection", target_ip)
        )

        if "html" in headers.get("content-type", "").lower():
            html_body = response.text[:_MAX_HTML_BODY_CHARS]
            candidates.extend(
                self._to_targets(extract_from_html_links(html_body), "html_link", target_ip)
            )

        return candidates

    @staticmethod
    def _to_targets(
        found: list[tuple[str, str]], source: str, target_ip: str
    ) -> list[DiscoveredTarget]:
        return [
            DiscoveredTarget(
                host=candidate,
                source=source,
                confidence=_CONFIDENCE_BY_SOURCE[source],
                discovered_from=target_ip,
                evidence=[detail],
            )
            for candidate, detail in found
        ]
