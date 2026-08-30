# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : reconstruire le graphe d'architecture a partir des hosts
deja scannes (OMEGA-DEEP_SPECIFICATIONS.md §6.2). Delegation directe a
domain/architecture/service.py — les interfaces (CLI/TUI) n'appellent que
l'application/, jamais le domaine directement, meme si ce use case n'a
pas d'autre dependance (port/repository) a orchestrer autour."""
from __future__ import annotations

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.architecture.service import reconstruct_architecture as _reconstruct
from omega_deep.domain.targets.models import Host


def reconstruct_architecture(hosts: list[Host]) -> ArchitectureGraph:
    return _reconstruct(hosts)
