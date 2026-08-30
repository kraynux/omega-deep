# Copyright (c) 2026 kraynux - Licence MIT
"""Point d'entree du package (`python -m omega_deep` et le script console
`omega-deep`). Dispatche vers le TUI (aucun argument) ou le CLI (au moins
un argument) — meme patron que omega-check/omega-scan/omega-stress
(D-007/D-008)."""
from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from omega_deep.app.bootstrap import bootstrap

    effective_argv = sys.argv[1:] if argv is None else argv
    is_tui = not effective_argv
    # console_logging=False sous le TUI : Textual controle l'ecran en mode
    # alternatif, une ecriture de log directe sur stderr corromprait son
    # rendu (voir app/bootstrap.py).
    container = bootstrap(console_logging=not is_tui)
    try:
        if is_tui:
            from omega_deep.interfaces.tui.app import OmegaDeepApp

            OmegaDeepApp(container).run()
            return 0

        from omega_deep.interfaces.cli.main import run as run_cli

        return run_cli(container, effective_argv)
    finally:
        container.close()


if __name__ == "__main__":
    raise SystemExit(main())
