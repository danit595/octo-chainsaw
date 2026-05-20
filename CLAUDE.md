# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Setup, run, and packaging (PowerShell on Windows 10/11; Python 3.10+):

```powershell
pip install -r requirements.txt
python autoclicker.py                  # run the GUI
python -m octoautoclicker               # equivalent, once src/ is on the path
pyinstaller AutoClicker.spec            # build dist\OctoAutoClicker.exe
```

Tests use pytest. There is no `pyproject.toml` or `pytest.ini` — `tests/conftest.py` injects `src/` onto `sys.path`, so always invoke pytest from the repo root:

```powershell
pytest                                  # whole suite
pytest tests/test_macros.py             # one file
pytest tests/test_macros.py::test_name  # one test
pytest -k "sequence and not smoke"      # by keyword
```

There is no configured linter or formatter — do not invent commands for them.

## Architecture

The app is a single-process Tk/CustomTkinter GUI driving three background-thread engines through a central controller. Understanding the controller wiring is the fastest path to making changes.

**Layered layout** (under `src/octoautoclicker/`):

- `models.py` — pure dataclasses (`ClickConfig`, `SequenceStep`, `Profile`, `Macro`, `MacroEvent`, `HotkeyConfig`, `Stats`) with `to_dict`/`from_dict`. These are the wire format for all on-disk JSON (profiles, macros, settings, stats) and the contract between UI and engines. `from_dict` filters unknown keys via `__dataclass_fields__`, which is the forward-compat strategy — new fields must have defaults.
- `config.py` — `ConfigStore` persists settings/profiles/stats under `%APPDATA%\OctoAutoClicker` on Windows (`~/.config/OctoAutoClicker` elsewhere). Macros live as individual JSON files under `<data_dir>/macros/`. Loaders swallow `JSONDecodeError`/`OSError` and return defaults rather than raising.
- `engines/` — headless, callback-driven, thread-owning. Each engine takes `on_state_change` / `on_error` / progress hooks at construction; **callbacks fire on the worker thread** and the controller is responsible for marshalling onto Tk's main loop. Optional deps (`pyautogui`, `mouse`, `keyboard`, `pygetwindow`, `pystray`) are guarded with `try/except` at import time and degrade gracefully (engines refuse to start and emit an error toast).
  - `clicker.ClickerEngine` — the click loop (jitter, region mode, sequence cycling, target-window/pixel gating).
  - `macros.MacroRecorder` / `MacroPlayer` plus `save_macro` / `load_macro` / `list_macros` / `delete_macro` helpers.
  - `hotkeys.HotkeyManager` — wraps the `keyboard` lib; rebinds from a `HotkeyConfig` on every settings change.
  - `tray.TrayIcon` — `pystray` integration; uses lambdas back to the controller.
- `ui/` — CustomTkinter views, one per sidebar tab. `MainWindow` hosts a sidebar plus a content frame and exposes `register_view(key, label, icon, frame)`. Views never touch engines directly — they expose callbacks to the controller and offer `apply_config` / `set_running` / `update_palette` methods. `theme.py` produces a `palette` dict from `(theme, accent)`; views must implement `update_palette` for live re-theming.
- `app.App` — the controller. It owns the `ConfigStore`, all engines, all views, the tray, the optional `MiniController`, and session-tracking state (`_session_clicks`, `_session_started_at`, `_cps_window`). All cross-component flow goes through here; engines and views are otherwise unaware of each other.

**Threading rule.** Every engine callback delegates back to the UI through `App._on_main_thread(fn)`, which calls `self.window.after(0, fn)`. New engine callbacks must follow the same pattern — never touch Tk widgets from a worker thread.

**Entry points.** `autoclicker.py` is a shim that prepends `src/` to `sys.path` then calls `octoautoclicker.app.main`. `src/octoautoclicker/__main__.py` exists so `python -m octoautoclicker` works once the package is importable. Both ultimately construct `App()` and call `.run()` (which is `window.mainloop()`).

**Build.** `AutoClicker.spec` is hand-maintained — it lists every `octoautoclicker.*` submodule under `hiddenimports` and bundles the CustomTkinter assets and `assets/` directory as `datas`. New top-level modules under `src/octoautoclicker/` must be added to that list or the bundled `.exe` will fail at import time.

**Hotkeys (defaults, all user-configurable in Settings):** F6 toggle clicker, F7 toggle recording, F8 toggle playback, ESC emergency stop. PyAutoGUI's failsafe (mouse to a screen corner aborts) is also wired and toggled by `AppSettings.failsafe_enabled`.
