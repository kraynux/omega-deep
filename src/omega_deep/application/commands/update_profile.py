# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : modifier un profil utilisateur existant. Identique a
omega-check."""
from __future__ import annotations

from omega_deep.domain.profiles.exceptions import ProfileNotFoundError
from omega_deep.domain.profiles.models import Profile
from omega_deep.domain.profiles.policies import normalize_ports, validate_ports
from omega_deep.ports.profile_repository import ProfileRepository


def update_profile(
    repo: ProfileRepository,
    name: str,
    description: str | None = None,
    ports: list[int] | None = None,
) -> Profile:
    existing = repo.load_user_profiles()
    current = existing.get(name)
    if current is None:
        raise ProfileNotFoundError(name)

    if ports is not None:
        validate_ports(ports)
        current.ports = normalize_ports(ports)
    if description is not None:
        current.description = description

    repo.save_user_profiles(existing)
    return current
