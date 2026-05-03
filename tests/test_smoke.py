"""Boot smoke tests — make sure the App starts and core modules import."""

from __future__ import annotations

import importlib
import os
import threading

import pytest

NEEDS_DISPLAY = pytest.mark.skipif(
    os.environ.get("OCTO_SKIP_GUI") == "1" or os.name not in ("nt",),
    reason="GUI smoke test requires a Windows display",
)

CORE_MODULES = [
    "octoautoclicker",
    "octoautoclicker.models",
    "octoautoclicker.config",
    "octoautoclicker.engines.clicker",
    "octoautoclicker.engines.macros",
    "octoautoclicker.engines.hotkeys",
    "octoautoclicker.engines.tray",
]

UI_MODULES = [
    "octoautoclicker.ui.theme",
    "octoautoclicker.ui.widgets",
    "octoautoclicker.ui.main_window",
    "octoautoclicker.ui.clicker_view",
    "octoautoclicker.ui.macro_view",
    "octoautoclicker.ui.macro_editor",
    "octoautoclicker.ui.mini_controller",
    "octoautoclicker.ui.sequence_view",
    "octoautoclicker.ui.profiles_view",
    "octoautoclicker.ui.settings_view",
    "octoautoclicker.ui.stats_view",
    "octoautoclicker.ui.about_view",
    "octoautoclicker.app",
]


@pytest.mark.parametrize("module", CORE_MODULES)
def test_core_modules_importable(module: str) -> None:
    importlib.import_module(module)


@pytest.mark.parametrize("module", UI_MODULES)
def test_ui_modules_importable(module: str) -> None:
    pytest.importorskip("customtkinter")
    importlib.import_module(module)


@NEEDS_DISPLAY
def test_app_boots_and_destroys() -> None:
    pytest.importorskip("customtkinter")
    pytest.importorskip("PIL")
    from octoautoclicker.app import App

    app = App()

    def kill() -> None:
        try:
            app.window.after(0, app.window.destroy)
        except Exception:
            pass

    threading.Timer(0.8, kill).start()
    app.run()
