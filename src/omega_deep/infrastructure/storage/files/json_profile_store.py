# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation JSON du ProfileRepository. Identique a omega-check."""
from __future__ import annotations

import json
from pathlib import Path

from omega_deep.domain.profiles.models import Profile


class JsonProfileStore:
    """Implemente ports/profile_repository.py::ProfileRepository."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load_user_profiles(self) -> dict[str, Profile]:
        if not self._path.exists():
            return {}

        raw = json.loads(self._path.read_text(encoding="utf-8"))
        return {
            name: Profile(
                name=entry["name"],
                description=entry["description"],
                ports=list(entry["ports"]),
                pinned=entry.get("pinned", False),
                origin=entry.get("origin", "user"),
            )
            for name, entry in raw.items()
        }

    def save_user_profiles(self, profiles: dict[str, Profile]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            name: {
                "name": profile.name,
                "description": profile.description,
                "ports": profile.ports,
                "pinned": profile.pinned,
                "origin": profile.origin,
            }
            for name, profile in profiles.items()
        }
        self._path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
