# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation TCP connect scan du port PortProber (ports/port_prober.py).
Identique a omega-check.

- Connexion etablie ou RST clair (ECONNREFUSED) -> resultat certain -> VERIFIED.
- Timeout persistant apres retries -> comportement typique d'un filtrage
  reseau, mais pas une certitude -> INFERRED, jamais VERIFIED.
"""
from __future__ import annotations

import socket

from omega_deep.core.enums import ConfidenceLevel, PortState
from omega_deep.domain.services.models import Port


class TcpPortProber:
    """Implemente ports/port_prober.py::PortProber."""

    def probe(
        self,
        target_ip: str,
        port: int,
        protocol: str,
        timeout: float,
        retries: int,
    ) -> Port:
        if protocol != "tcp":
            raise NotImplementedError(f"protocole non supporte : {protocol!r}")

        last_timeout = False
        for attempt in range(retries + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                try:
                    sock.connect((target_ip, port))
                except ConnectionRefusedError:
                    return Port(
                        port_number=port,
                        protocol=protocol,
                        state=PortState.CLOSED,
                        state_confidence=ConfidenceLevel.VERIFIED,
                        evidence=["ECONNREFUSED (RST recu)"],
                    )
                except TimeoutError:
                    last_timeout = True
                    continue
                except OSError as exc:
                    return Port(
                        port_number=port,
                        protocol=protocol,
                        state=PortState.FILTERED,
                        state_confidence=ConfidenceLevel.INFERRED,
                        evidence=[f"erreur reseau : {exc}"],
                    )
                else:
                    return Port(
                        port_number=port,
                        protocol=protocol,
                        state=PortState.OPEN,
                        state_confidence=ConfidenceLevel.VERIFIED,
                        evidence=["connexion TCP etablie"],
                    )

        evidence = (
            f"timeout apres {retries + 1} tentative(s)" if last_timeout else "aucune reponse"
        )
        return Port(
            port_number=port,
            protocol=protocol,
            state=PortState.FILTERED,
            state_confidence=ConfidenceLevel.INFERRED,
            evidence=[evidence],
        )
