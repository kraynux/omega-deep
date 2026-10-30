# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation socket du port VncProber (protocole RFB, RFC 6143).
Identique a omega-check.

S'arrete juste apres la negociation des security types, avant toute
tentative d'authentification (sonde passive, pas d'identifiants a essayer)."""
from __future__ import annotations

import re
import socket
import struct

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.services.models import Service
from omega_deep.domain.services.policies import classify_vnc_security
from omega_deep.shared.i18n import _

_VERSION_RE = re.compile(rb"^RFB (\d{3})\.(\d{3})\n$")


class SocketVncProber:
    """Implemente ports/vnc_prober.py::VncProber."""

    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        try:
            with socket.create_connection((target_ip, port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                banner = _recv_exact(sock, 12)
                match = _VERSION_RE.match(banner)
                if not match:
                    return Service(evidence=[_("banner inattendu (pas RFB) : {banner!r}").format(banner=banner)])

                major, minor = int(match.group(1)), int(match.group(2))
                sock.sendall(banner)  # on reconduit la version du serveur, toujours valide (RFC 6143 §7.1.1)

                security_types = _read_security_types(sock, major, minor)
        except OSError as exc:
            return Service(evidence=[_("échec de connexion VNC : {exc}").format(exc=exc)])

        if security_types is None:
            return Service(
                protocol_name="VNC",
                protocol_confidence=ConfidenceLevel.VERIFIED,
                version=f"{major}.{minor}",
                version_confidence=ConfidenceLevel.VERIFIED,
                evidence=[_("RFB {major}.{minor} : négociation des security types échouée/refusée").format(major=major, minor=minor)],
            )

        auth_required, type_names = classify_vnc_security(security_types)
        return Service(
            protocol_name="VNC",
            protocol_confidence=ConfidenceLevel.VERIFIED,
            version=f"{major}.{minor}",
            version_confidence=ConfidenceLevel.VERIFIED,
            auth_required=auth_required,
            auth_required_confidence=ConfidenceLevel.VERIFIED if type_names else ConfidenceLevel.UNKNOWN,
            auth_types=type_names,
            auth_types_confidence=ConfidenceLevel.VERIFIED if type_names else ConfidenceLevel.UNKNOWN,
            evidence=[_("RFB {major}.{minor}, security types : {type_names}").format(major=major, minor=minor, type_names=type_names)],
        )


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            break
        data += chunk
    return data


def _read_security_types(sock: socket.socket, major: int, minor: int) -> list[int] | None:
    if (major, minor) >= (3, 7):
        count_byte = _recv_exact(sock, 1)
        if not count_byte:
            return None
        count = count_byte[0]
        if count == 0:
            return None  # connexion refusee, raison textuelle ignoree (sonde passive)
        types = _recv_exact(sock, count)
        return list(types)

    # RFB <= 3.3 : un seul type de securite, encode sur 4 octets big-endian.
    raw = _recv_exact(sock, 4)
    if len(raw) < 4:
        return None
    (security_type,) = struct.unpack(">I", raw)
    if security_type == 0:
        return None
    return [security_type]
