# OctoAutoClicker v2.0

A modern, modular auto-clicker and macro recorder for Windows with a polished
dark/light interface, configurable hotkeys, jitter randomization, profile
presets, and lifetime stats.

![version](https://img.shields.io/badge/version-2.0.0-8B5CF6)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey)
![license](https://img.shields.io/badge/license-MIT-green)

## What's new in v2

### Visual & UX overhaul
- New CustomTkinter-based interface with sidebar navigation, cards, status
  pills, and toast notifications.
- Dark and light themes with five accent colors (violet, cyan, emerald, rose,
  amber). Theme changes apply live.
- Live clicks-per-second meter with a 5-second rolling window.
- Status pill showing idle / clicking / recording / playing at a glance.
- Toast notifications instead of disruptive modal dialogs.

### Clicker engine
- Configurable timing jitter (ms) and position jitter (px) for natural-looking
  clicks.
- Loop or fixed-count repeat modes.
- Click at the cursor or a captured fixed coordinate. New "Pick" button uses a
  3-second countdown so you can position the cursor without touching the
  keyboard.
- Pyautogui failsafe is preserved; engine recovers gracefully and surfaces
  errors as toasts.

### Macro engine
- Records mouse moves, button presses, and keyboard events.
- Playback supports speed multipliers and loop counts.
- Import and export macros as JSON files.
- Macros, profiles, settings, and stats persist under
  `%APPDATA%\OctoAutoClicker`.

### Productivity
- Save and recall named **Profiles** for click configurations.
- Customize all four global hotkeys from the Settings tab.
- Lifetime stats: total clicks, sessions, active time, macros played.

## Hotkeys (defaults)

| Key | Action            |
| --- | ----------------- |
| F6  | Toggle clicking   |
| F7  | Toggle recording  |
| F8  | Toggle playback   |
| ESC | Emergency stop    |

All hotkeys are user-configurable in **Settings**.

## Install / run from source

```powershell
pip install -r requirements.txt
python autoclicker.py
```

Requires Python 3.10+.

## Build a Windows executable

```powershell
pip install -r requirements.txt
pyinstaller AutoClicker.spec
```

The bundled `.exe` lands in `dist\OctoAutoClicker.exe` and ships the
CustomTkinter assets.

## Project layout

```
autoclicker.py              # entry-point shim (adds src/ to sys.path)
src/octoautoclicker/
  app.py                    # App controller wiring UI + engines
  config.py                 # settings, profiles, stats persistence
  models.py                 # typed dataclasses
  engines/
    clicker.py              # threaded auto-clicker with jitter
    macros.py               # recorder + player
    hotkeys.py              # configurable global hotkeys
  ui/
    main_window.py          # sidebar + content host
    clicker_view.py         # auto-clicker page
    macro_view.py           # macro page
    profiles_view.py        # profile gallery
    settings_view.py        # appearance, hotkeys, behavior
    stats_view.py           # lifetime stats + cheatsheet
    theme.py                # palette and fonts
    widgets.py              # cards, tiles, sidebar buttons, toasts
tests/
  test_models.py
  test_config.py
  test_macros.py
```

## Safety

- PyAutoGUI failsafe: move the mouse to a screen corner to instantly stop.
- ESC triggers an emergency stop across clicker, recorder, and player.
- All recorded macros are stored as plain JSON for inspection and editing.

## License

MIT — see [LICENSE](LICENSE).
