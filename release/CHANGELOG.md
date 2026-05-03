# Changelog

## v2.0.0
### Major upgrade — new UI and engine

#### UI / UX
- Rewritten interface using CustomTkinter with sidebar navigation, cards,
  status pills, and toast notifications.
- Dark and light themes with five accent colors that apply live.
- Live clicks-per-second meter; large, glanceable click counter.
- Replaced disruptive modal popups with non-blocking toasts.
- New tabs: Auto Clicker, Macros, Profiles, Settings, Stats.

#### Clicker engine
- Threaded engine with callbacks decoupled from the UI.
- Timing jitter (ms) and position jitter (px) for natural clicks.
- Loop or fixed-count repeat modes.
- 3-second cursor capture mode for fixed-position clicks.

#### Macro engine
- Captures mouse moves, button presses, and keyboard events.
- Playback supports speed multipliers and loop counts.
- Import / export macros as JSON.

#### Productivity
- Saveable named Profiles for click configurations.
- All four global hotkeys configurable in Settings.
- Lifetime stats persisted under `%APPDATA%\OctoAutoClicker`.

#### Engineering
- Modular `src/octoautoclicker` package with engines, models, and UI layers.
- Type-hinted dataclasses for all persistent state.
- Pytest suite covering models, config persistence, and macro round-trip.
- Updated PyInstaller spec bundles CustomTkinter assets.

## v1.0.1
- Initial release with auto-clicking and macro recording.
