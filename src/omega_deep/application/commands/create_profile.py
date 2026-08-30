# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : creer un profil utilisateur. Identique a omega-check."""
from __future__ import annotations

from omega_deep.domain.profiles.defaults import RESERVED_NAMES
from omega_deep.domain.profiles.exceptions import DomainError
from omega_deep.domain.profiles.models import Profile
from omega_deep.domain.profiles.policies import (
    ensure_name_not_reserved,
    normalize_ports,
    validate_ports,
)
from omega_deep.ports.profile_repository import ProfileRepository


class ProfileAlreadyExistsError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Un profil utilisateur '{name}' existe deja")
        self.name = name


def create_profile(
    repo: ProfileRepository,
    name: str,
    description: str,
    ports: list[int],
    pinned: bool = False,
) -> Profile:
    ensure_name_not_reserved(name, RESERVED_NAMES)
    validate_ports(ports)

    existing = repo.load_user_profiles()
    if name in existing:
        raise ProfileAlreadyExistsError(name)

    profile = Profile(
        name=name,
        description=description,
        ports=normalize_ports(ports),
        pinned=pinned,
        origin="user",
    )
    existing[name] = profile
    repo.save_user_profiles(existing)
    return profile
