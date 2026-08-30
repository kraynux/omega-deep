# Copyright (c) 2026 kraynux - Licence MIT
"""Configuration du logger applicatif technique (stdlib logging). Meme
patron que omega-check : `application/commands/{run_scan,scan_host}.py`
emettent deja des `logging.getLogger("omega_deep.scan").info(...)`, sans
handler de fichier configure nulle part ils ne survivraient pas au-dela
du processus. `console=False` pour le TUI (Textual controle l'ecran en
mode alternatif, une ecriture directe sur stderr corromprait son rendu)."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

LOGGER_NAME = "omega_deep"
APP_LOG_FILENAME = "app.log"
DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(
    *, log_path: Path, level: int = logging.INFO, console: bool = True
) -> logging.Logger:
    """Configure et retourne le logger applicatif nomme 'omega_deep', avec
    un handler fichier et (si `console=True`) un handler console.
    Idempotent : rappeler cette fonction remplace les handlers existants
    plutot que d'en accumuler (utile en tests)."""
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
