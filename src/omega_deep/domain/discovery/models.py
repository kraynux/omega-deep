# Copyright (c) 2026 kraynux - Licence MIT
"""Bounded context 'discovery' : cibles decouvertes a partir d'indices
observes sur une cible deja scannee (OMEGA-DEEP_SPECIFICATIONS.md §4.2/§6.2).

C'est la partie la plus sensible d'OMEGA-DEEP (cibles non explicitement
demandees par l'utilisateur au depart) — voir domain/discovery/policies.py
pour les garde-fous, et ~/DEV/SUITE/DECISIONS_ARCHITECTURE.md D-003 pour
le flux de validation complet."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from omega_deep.core.enums import ConfidenceLevel


class DiscoveryState(str, Enum):
    """Machine a etats d'une cible decouverte (D-003) :

    PROPOSED   -> extraite par un DiscoveryProber, pas encore montree.
    PRESENTED  -> affichee a l'utilisateur avec tout le contexte de decision.
    ACCEPTED   -> validee explicitement par l'utilisateur, PAR CIBLE.
    REJECTED   -> refusee explicitement, OU refus implicite (fail-safe :
                  toute cible encore PRESENTED quand l'utilisateur quitte
                  l'ecran de validation, ou en cas de timeout/interruption,
                  passe automatiquement ici — le silence n'est jamais une
                  acceptation).
    SCANNED    -> uniquement les cibles ACCEPTED passent au pipeline de scan.
    """

    PROPOSED = "proposed"
    PRESENTED = "presented"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SCANNED = "scanned"


@dataclass
class DiscoveredTarget:
    """Une cible potentielle, extraite d'un indice observe sur un host deja
    scanne. `host` est deja normalise (domain/targets/validation.py::
    normalize_target_input) mais pas forcement resolu — voir
    domain/discovery/policies.py pour la garde de perimetre (subnet/IP
    privee) qui determine si cette cible est meme proposee."""

    host: str
    source: str  # "header", "redirection", "certificate", "html_link"
    confidence: ConfidenceLevel
    discovered_from: str  # IP du host qui a permis la decouverte
    state: DiscoveryState = DiscoveryState.PROPOSED
    evidence: list[str] = field(default_factory=list)
