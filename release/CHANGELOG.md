# Changelog

## v2.2.0
### Quality-of-life pass
- **CPS slider** on the Auto Clicker tab — drag to set 1-50 clicks/sec; wires
  back into the interval fields.
- **Profile import / export** as JSON, plus an Import button on the Profiles
  page header and per-card Export.
- **Macro library search** — live substring filter above the list.
- **Mini view** — compact always-on-top floating controller with start/stop,
  status dot, live CPS and total click counter, and a button to restore the
  main window. Toggled from the new sidebar action.
- **About** page with what-it-does, tips, and dependency credits.
- App boots are now covered by a smoke test (see tests/test_smoke.py).

## v2.1.0
### More UX wins on top of v2.0
- New **Click Sequence** tab and engine: queue of (x, y, button, type, delay)
  steps cycled per iteration. Profiles persist sequences alongside other
  click settings.
- **Targeting** card: optional active-window substring filter and pixel-color
  trigger (with a "Sample (3s)" helper that captures the screen pixel under
  the cursor).
- **In-app macro editor** (Toplevel) — retime or delete events without
  re-recording.
- **System tray icon** with show / toggle clicker / emergency stop / quit
  actions, generated programmatically from the active accent color.
- Multi-resolution **app icon** (16-256 px) bundled into both the window and
  the PyInstaller spec.
- Tests added for sequence persistence, sequence dispatch, and color
  parsing.

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
