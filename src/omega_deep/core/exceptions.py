# Copyright (c) 2026 kraynux - Licence MIT
"""Racine absolue des exceptions du projet.

Porte le meme motif que omega-check/omega-scan/omega-stress (D-007) :
chaque couche a sa propre racine (domain/errors.py::DomainError,
application/exceptions.py::ApplicationError, etc.), toutes derivees de
celle-ci — un `except OmegaDeepError` generique attrape donc toute erreur
du projet, quelle que soit sa couche d'origine."""
from __future__ import annotations


class OmegaDeepError(Exception):
    """Racine absolue des erreurs omega-deep."""


class ConfigurationError(OmegaDeepError):
    """Configuration invalide ou incomplete (chemins, variables d'environnement)."""
