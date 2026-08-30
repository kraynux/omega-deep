# Copyright (c) 2026 kraynux - Licence MIT
"""Erreurs du bounded context 'profiles'. Identique a omega-check."""
from __future__ import annotations

from omega_deep.domain.errors import DomainError


class InvalidPortError(DomainError):
    """Un port du profil est hors de la plage 1-65535."""

    def __init__(self, port: int) -> None:
        super().__init__(f"Port hors plage (1-65535) : {port}")
        self.port = port


class DuplicatePortsError(DomainError):
    """La liste de ports d'un profil contient des doublons."""

    def __init__(self, duplicates: list[int]) -> None:
        super().__init__(f"Ports en double : {sorted(duplicates)}")
        self.duplicates = duplicates


class ReservedProfileNameError(DomainError):
    """Le nom demande pour un profil utilisateur est reserve aux profils systeme."""

    def __init__(self, name: str) -> None:
        super().__init__(f"'{name}' est un nom de profil systeme reserve")
        self.name = name


class ProfileNotFoundError(DomainError):
    """Aucun profil (systeme ou utilisateur) ne porte ce nom."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Profil introuvable : '{name}'")
        self.name = name
