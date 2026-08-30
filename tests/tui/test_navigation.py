# Copyright (c) 2026 kraynux - Licence MIT
"""Tests structurels du TUI (Textual Pilot) : verifie que l'app demarre et
que chaque ecran du menu principal s'ouvre/se ferme sans exception —
aucune verification visuelle (voir memoire de session : le pipeline
SVG->rsvg-convert->PNG est connu peu fiable pour ce jeu de caracteres,
une verification visuelle reelle se fait en direct avec l'utilisateur,
pas ici)."""
from __future__ import annotations

from pathlib import Path

import pytest

from omega_deep.app.bootstrap import bootstrap
from omega_deep.interfaces.tui.app import OmegaDeepApp
from omega_deep.interfaces.tui.screens.help_screen import HelpScreen
from omega_deep.interfaces.tui.screens.history import HistoryScreen
from omega_deep.interfaces.tui.screens.home import HomeScreen
from omega_deep.interfaces.tui.screens.profiles_screen import ProfilesScreen
from omega_deep.interfaces.tui.screens.scan_setup import ScanSetupScreen
from omega_deep.interfaces.tui.screens.settings_screen import SettingsScreen
from omega_deep.interfaces.tui.screens.splash import SplashScreen


@pytest.fixture
def app(tmp_path: Path) -> OmegaDeepApp:
    container = bootstrap(var_dir=tmp_path, console_logging=False)
    app = OmegaDeepApp(container)
    app._test_container = container  # type: ignore[attr-defined]
    return app


async def test_splash_then_home(app: OmegaDeepApp) -> None:
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, SplashScreen)
        await pilot.press("space")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)
    app._test_container.close()  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("button_id", "expected_screen"),
    [
        ("scan", ScanSetupScreen),
        ("profiles", ProfilesScreen),
        ("history", HistoryScreen),
        ("settings", SettingsScreen),
        ("help", HelpScreen),
    ],
)
async def test_home_menu_opens_and_closes_each_screen(
    app: OmegaDeepApp, button_id: str, expected_screen: type
) -> None:
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        await pilot.press("space")  # dismiss splash
        await pilot.pause()

        await pilot.click(f"#{button_id}")
        await pilot.pause()
        assert isinstance(app.screen, expected_screen)

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)
    app._test_container.close()  # type: ignore[attr-defined]
