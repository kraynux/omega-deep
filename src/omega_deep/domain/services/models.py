# Copyright (c) 2026 kraynux - Licence MIT
"""Bounded context 'services' : ports TCP/UDP, services identifies dessus,
roles inferes et pile protocolaire. Identique a omega-check."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_deep.core.enums import ConfidenceLevel, PortState


@dataclass
class RoleElement:
    role: str
    software: str | None = None
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    evidence: list[str] = field(default_factory=list)


@dataclass
class TransportLayer:
    order: int
    layer_type: str  # "network", "transport", "security", "application"
    protocol: str
    software: str | None = None
    version: str | None = None
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    evidence: list[str] = field(default_factory=list)


@dataclass
class Service:
    # Identification de base
    protocol_name: str | None = None
    protocol_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN

    # Logiciel / version (DECLARED par defaut : annonce par la cible,
    # falsifiable — voir D-001)
    software: str | None = None
    software_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    version: str | None = None
    version_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN

    # Role
    role: str | None = None
    role_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    role_chain: list[RoleElement] = field(default_factory=list)

    # Authentification
    auth_required: bool | None = None
    auth_required_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    auth_types: list[str] = field(default_factory=list)
    auth_types_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    auth_details: dict = field(default_factory=dict)

    # Firewall / WAF applicatif
    firewall_app_present: bool | None = None
    firewall_app_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    waf_present: bool | None = None
    waf_name_guess: str | None = None
    waf_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN

    # TLS / chiffrement
    tls_library: str | None = None
    tls_library_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    tls_version: str | None = None
    tls_version_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    tls_cipher: str | None = None
    tls_cipher_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    tls_cert_subject: str | None = None
    tls_cert_issuer: str | None = None
    tls_cert_san: list[str] = field(default_factory=list)

    # Pile protocolaire / encapsulation
    encapsulation_layers: list[TransportLayer] = field(default_factory=list)

    # Preuves / indices
    evidence: list[str] = field(default_factory=list)


@dataclass
class Port:
    port_number: int
    protocol: str  # "tcp", "udp"
    state: PortState
    state_confidence: ConfidenceLevel
    evidence: list[str] = field(default_factory=list)
    service: Service | None = None
