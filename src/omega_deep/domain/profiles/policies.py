# Copyright (c) 2026 kraynux - Licence MIT
"""Regles de validation des profils (voir OMEGA-DEEP_SPECIFICATIONS.md §3).
Identique a omega-check.

- Ports entre 1 et 65535.
- Pas de doublons dans la liste des ports.
- Noms reserves pour les profils systeme.
"""
from __future__ import annotations

from collections import Counter

from omega_deep.domain.profiles.exceptions import (
    DuplicatePortsError,
    InvalidPortError,
    ReservedProfileNameError,
)

MIN_PORT = 1
MAX_PORT = 65535


def validate_ports(ports: list[int]) -> None:
    """Leve InvalidPortError ou DuplicatePortsError si la liste est invalide.
    Ne renvoie rien : appelee pour son effet de bord (raise) avant toute
    creation/modification de profil."""
    for port in ports:
        if not (MIN_PORT <= port <= MAX_PORT):
            raise InvalidPortError(port)

    counts = Counter(ports)
    duplicates = [port for port, count in counts.items() if count > 1]
    if duplicates:
        raise DuplicatePortsError(duplicates)


def normalize_ports(ports: list[int]) -> list[int]:
    """Trie et deduplique — utilise pour le profil 'complet' et pour
    normaliser un profil utilisateur avant stockage. Ne valide pas la
    plage : appeler validate_ports() separement si necessaire."""
    return sorted(set(ports))


def ensure_name_not_reserved(name: str, reserved_names: frozenset[str]) -> None:
    """Leve ReservedProfileNameError si `name` est un nom de profil systeme
    (interdit pour un profil utilisateur)."""
    if name in reserved_names:
        raise ReservedProfileNameError(name)


def parse_port_spec(raw: str) -> list[int]:
    """'80' / '22,443,8080' / '1000-2000' (et combinaisons, ex.
    '22,80,1000-2000') -> liste de ports normalisee (triee, sans doublons).

    Leve ValueError sur un token non numerique/non-plage (message
    utilisateur construit par l'appelant), InvalidPortError/
    DuplicatePortsError via validate_ports() sur la plage/les doublons."""
    ports: list[int] = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_str, _, end_str = token.partition("-")
            start, end = int(start_str), int(end_str)
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(token))

    validate_ports(ports)
    return normalize_ports(ports)
