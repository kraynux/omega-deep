# Copyright (c) 2026 kraynux - Licence MIT
"""Resolution des chemins runtime (var/), la seule source de verite pour
ces chemins. Meme patron que omega-check/omega-scan/omega-stress : tout
doit vivre par defaut dans le dossier de l'application (`./var`), rien
dans le filesystem utilisateur, sauf override explicite
(`$OMEGA_DEEP_VAR_DIR`)."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_VAR_DIRNAME = "var"
ENV_VAR_DIR = "OMEGA_DEEP_VAR_DIR"


def resolve_var_dir() -> Path:
    """Racine des fichiers runtime : `$OMEGA_DEEP_VAR_DIR` si defini,
    sinon `./var` relatif au repertoire courant d'execution."""
    override = os.environ.get(ENV_VAR_DIR)
    if override:
        return Path(override)
    return Path.cwd() / DEFAULT_VAR_DIRNAME


def default_db_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "db" / "omega-deep.db"


def default_profiles_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "user_profiles.json"


def default_settings_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "settings.json"


def default_exports_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "exports"


def default_screenshots_dir(var_dir: Path | None = None) -> Path:
    """Sans ce chemin explicite, `App.deliver_screenshot()` ecrirait par
    defaut dans le dossier Telechargements de l'utilisateur, jamais dans
    var/ — meme piege deja documente et corrige cote omega-check/omega-stress."""
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "screenshots"
