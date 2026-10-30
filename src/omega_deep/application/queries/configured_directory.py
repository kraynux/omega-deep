# Copyright (c) 2026 kraynux - Licence MIT
"""Dossier d'exports / de captures effectif : le chemin choisi dans Reglages s'il est rempli,
sinon le dossier par defaut (var/exports, var/screenshots). Correctif 2026-10-27 : le chemin
d'exports etait enregistre mais jamais relu (l'export allait toujours dans var/exports)."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omega_deep.ports.settings_store import SettingsStore

EXPORTS_DIR_KEY = "exports_dir_override"
SCREENSHOTS_DIR_KEY = "screenshots_dir_override"


def configured_directory(settings_store: SettingsStore, key: str, default: Path) -> Path:
    override = (settings_store.get(key, "") or "").strip()
    return Path(override).expanduser() if override else default
