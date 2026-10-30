# Copyright (c) 2026 kraynux - Licence MIT
"""Erreurs du bounded context 'profiles'. Identique a omega-check."""
from __future__ import annotations

from omega_deep.domain.errors import DomainError
from omega_deep.shared.i18n import _


class InvalidPortError(DomainError):
    """Un port du profil est hors de la plage 1-65535."""

    def __init__(self, port: int) -> None:
        super().__init__(_("Port hors plage (1-65535) : {port}").format(port=port))
        self.port = port


class DuplicatePortsError(DomainError):
    """La liste de ports d'un profil contient des doublons."""

    def __init__(self, duplicates: list[int]) -> None:
        super().__init__(_("Ports en double : {value}").format(value=sorted(duplicates)))
        self.duplicates = duplicates


class ReservedProfileNameError(DomainError):
    """Le nom demande pour un profil utilisateur est reserve aux profils systeme."""

    def __init__(self, name: str) -> None:
        super().__init__(_("'{name}' est un nom de profil système réservé").format(name=name))
        self.name = name


class ProfileNotFoundError(DomainError):
    """Aucun profil (systeme ou utilisateur) ne porte ce nom."""

    def __init__(self, name: str) -> None:
        super().__init__(_("Profil introuvable : '{name}'").format(name=name))
        self.name = name
