# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : vider le dossier de captures d'ecran (ecran Reglages). Voir
clear_exports.py pour le raisonnement (housekeeping filesystem simple)."""
from __future__ import annotations

import shutil
from pathlib import Path


def clear_screenshots(screenshots_dir: Path) -> None:
    shutil.rmtree(screenshots_dir, ignore_errors=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)
