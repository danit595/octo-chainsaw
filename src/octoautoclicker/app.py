"""Application controller — wires the UI to the engines."""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path
from tkinter import filedialog
from typing import Callable

import customtkinter as ctk

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None

from . import __version__
from .config import AppSettings, ConfigStore
from .engines.clicker import ClickerEngine
from .engines.hotkeys import HotkeyManager
from .engines.macros import (
    MacroPlayer,
    MacroRecorder,
    delete_macro,
    list_macros,
    load_macro,
    save_macro,
)
from .engines.tray import TrayIcon
from .models import ClickConfig, Macro, Profile, SequenceStep, Stats
from .ui import theme as t
from .ui.about_view import AboutView
from .ui.clicker_view import ClickerView
from .ui.macro_editor import MacroEditor
from .ui.macro_view import MacroView
from .ui.main_window import MainWindow
from .ui.mini_controller import MiniController
from .ui.profiles_view import ProfilesView
from .ui.sequence_view import SequenceView
from .ui.settings_view import SettingsView
from .ui.stats_view import StatsView


class App:
    def __init__(self) -> None:
        self.store = ConfigStore()
        self.settings: AppSettings = self.store.load_settings()
        self.profiles: list[Profile] = self.store.load_profiles()
        self.stats: Stats = self.store.load_stats()
        self.palette = t.palette(self.settings.theme, self.settings.accent)

        ctk.set_appearance_mode("dark" if self.settings.theme == "dark" else "light")
        ctk.set_default_color_theme("blue")

        self.window = MainWindow(self.palette)
        self.window.on_close(self._on_close)

        # Engines
        self.clicker = ClickerEngine(
            on_click=self._on_click_count,
            on_state_change=self._on_clicker_state,
            on_error=self._on_engine_error,
        )
        self.recorder = MacroRecorder(on_state_change=self._on_recording_state)
        self.player = MacroPlayer(
            on_state_change=self._on_playback_state,
            on_error=self._on_engine_error,
        )
        self.hotkeys = HotkeyManager()
        self.tray = TrayIcon(
            on_show=lambda: self._on_main_thread(self._restore_window),
            on_toggle_clicker=lambda: self._on_main_thread(self._hotkey_toggle_clicker),
            on_emergency_stop=lambda: self._on_main_thread(self._emergency_stop),
            on_quit=lambda: self._on_main_thread(self._quit_app),
            accent=self.palette["primary"],
        )

        self._buffered_macro: Macro | None = None
        self._session_clicks = 0
        self._session_started_at: float | None = None
        self._sequence: list[SequenceStep] = []
        self._mini: MiniController | None = None
        self._cps_window: list[float] = []

        self._build_views()
        self._wire_hotkeys()
        self._refresh_all()
        self.window.show("clicker")
        if self.tray.start():
            pass

        if pyautogui is not None:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0

    # ---------- view setup ----------

    def _build_views(self) -> None:
        self.clicker_view = ClickerView(
            self.window.content,
            self.palette,
            on_start_stop=self._toggle_clicker,
            on_pick_position=self._pick_position,
            on_save_profile=self._save_current_profile,
        )
        self.macro_view = MacroView(
            self.window.content,
            self.palette,
            on_record_toggle=self._toggle_recording,
            on_save=self._save_buffered_macro,
            on_play=self._play_macro,
            on_stop=self._stop_playback,
            on_delete=self._delete_macro,
            on_export=self._export_macro,
            on_import=self._import_macro,
            on_edit=self._edit_macro,
        )
        self.sequence_view = SequenceView(
            self.window.content,
            self.palette,
            on_change=self._on_sequence_change,
            on_pick_position=self._pick_position,
        )
        self.profiles_view = ProfilesView(
            self.window.content,
            self.palette,
            on_apply=self._apply_profile,
            on_delete=self._delete_profile,
            on_export=self._export_profile,
            on_import=self._import_profile,
        )
        self.settings_view = SettingsView(
            self.window.content,
            self.palette,
            self.settings,
            on_change=self._on_settings_change,
        )
        self.stats_view = StatsView(self.window.content, self.palette)
        self.about_view = AboutView(self.window.content, self.palette)

        self.window.register_view("clicker", "Auto Clicker", "🎯", self.clicker_view)
        self.window.register_view("sequence", "Sequence", "⛓", self.sequence_view)
        self.window.register_view("macros", "Macros", "🎬", self.macro_view)
        self.window.register_view("profiles", "Profiles", "📚", self.profiles_view)
        self.window.register_view("settings", "Settings", "⚙", self.settings_view)
        self.window.register_view("stats", "Stats", "📊", self.stats_view)
        self.window.register_view("about", "About", "ⓘ", self.about_view)
        self.window.add_sidebar_action("⛶  Mini view", self._toggle_mini)

    def _refresh_all(self) -> None:
        # Apply last-used profile if it exists
        last = next(
            (p for p in self.profiles if p.name == self.settings.last_profile),
            None,
        )
        if last is None and self.profiles:
            last = self.profiles[0]
        if last is not None:
            self.clicker_view.apply_config(last.config)
            self._sequence = list(last.config.sequence or [])
            self.sequence_view.set_steps(self._sequence)

        self.profiles_view.set_profiles(self.profiles)
        self.macro_view.set_macros(list_macros(self.store.macros_dir))
        self.macro_view.set_buffer(self._buffered_macro)
        self.stats_view.update_stats(self.stats)
        self.stats_view.update_shortcuts(self.settings.hotkeys)

    # ---------- hotkeys ----------

    def _wire_hotkeys(self) -> None:
        self.hotkeys.bind("toggle_clicker", lambda: self._on_main_thread(self._hotkey_toggle_clicker))
        self.hotkeys.bind("toggle_recording", lambda: self._on_main_thread(self._toggle_recording))
        self.hotkeys.bind("toggle_playback", lambda: self._on_main_thread(self._hotkey_toggle_playback))
        self.hotkeys.bind("emergency_stop", lambda: self._on_main_thread(self._emergency_stop))
        ok = self.hotkeys.apply(self.settings.hotkeys)
        if not ok:
            self._toast("Some hotkeys could not be registered.", "warning")

    def _hotkey_toggle_clicker(self) -> None:
        cfg = self.clicker_view.get_config() if not self.clicker.running else None
        self._toggle_clicker(cfg)

    def _hotkey_toggle_playback(self) -> None:
        if self.player.playing:
            self._stop_playback()
        else:
            self.macro_view._play()  # use whatever's selected in the view

    # ---------- clicker ----------

    def _toggle_clicker(self, config: ClickConfig | None) -> None:
        if self.clicker.running:
            self.clicker.stop()
            return
        if config is None:
            self._toast("Invalid input — check the interval and counts.", "error")
            return
        self.clicker.reset_count()
        self._session_clicks = 0
        self._session_started_at = time.monotonic()
        if self.clicker.start(config):
            if self.settings.minimize_on_start:
                self.window.iconify()
            self._toast("Clicking started.", "success")

    def _toggle_mini(self) -> None:
        if self._mini is None or not self._mini.winfo_exists():
            self._mini = MiniController(
                self.window,
                self.palette,
                on_toggle=self._hotkey_toggle_clicker,
                on_emergency_stop=self._emergency_stop,
                on_open_main=self._restore_window,
            )
            self._mini.set_running(self.clicker.running)
        else:
            try:
                if self._mini.state() == "withdrawn":
                    self._mini.deiconify()
                else:
                    self._mini.lift()
                    self._mini.focus()
            except Exception:
                pass

    def _on_clicker_state(self, running: bool) -> None:
        self._on_main_thread(lambda: self.clicker_view.set_running(running))
        if self._mini is not None and self._mini.winfo_exists():
            self._on_main_thread(lambda r=running: self._mini.set_running(r))
        if not running and self._session_started_at is not None:
            elapsed = time.monotonic() - self._session_started_at
            self._session_started_at = None
            self.stats.total_sessions += 1
            self.stats.total_seconds_active += elapsed
            self.stats.total_clicks += self._session_clicks
            self._on_main_thread(lambda: self.stats_view.update_stats(self.stats))
            self.store.save_stats(self.stats)

    def _on_click_count(self, count: int) -> None:
        self._session_clicks = count
        now = time.monotonic()
        self._cps_window.append(now)
        cutoff = now - 5.0
        self._cps_window = [t_ for t_ in self._cps_window if t_ >= cutoff]
        if len(self._cps_window) >= 2:
            span = self._cps_window[-1] - self._cps_window[0]
            cps = (len(self._cps_window) - 1) / span if span > 0 else 0.0
        else:
            cps = 0.0
        self._on_main_thread(lambda c=count: self.clicker_view.update_count(c))
        if self._mini is not None and self._mini.winfo_exists():
            self._on_main_thread(lambda c=count, p=cps: self._mini.update_metrics(p, c))

    def _pick_position(self, callback: Callable[[int, int], None]) -> None:
        if pyautogui is None:
            self._toast("pyautogui not available — cannot pick position.", "error")
            return
        self.window.iconify()
        self._toast("Move mouse to target — capturing in 3 seconds.", "info", 2800)

        def capture() -> None:
            try:
                x, y = pyautogui.position()
            finally:
                self.window.deiconify()
            callback(int(x), int(y))
            self._toast(f"Captured ({int(x)}, {int(y)}).", "success")

        self.window.after(3000, capture)

    def _save_current_profile(self, config: ClickConfig) -> None:
        dialog = ctk.CTkInputDialog(
            title="Save profile", text="Profile name:"
        )
        name = dialog.get_input()
        if not name:
            return
        existing = next((p for p in self.profiles if p.name == name), None)
        if existing:
            existing.config = config
        else:
            self.profiles.append(Profile(name=name, config=config))
        self.store.save_profiles(self.profiles)
        self.settings.last_profile = name
        self.store.save_settings(self.settings)
        self.profiles_view.set_profiles(self.profiles)
        self._toast(f"Saved profile '{name}'.", "success")

    def _apply_profile(self, profile: Profile) -> None:
        self.clicker_view.apply_config(profile.config)
        self.settings.last_profile = profile.name
        self.store.save_settings(self.settings)
        self.window.show("clicker")
        self._toast(f"Applied profile '{profile.name}'.", "success")

    def _delete_profile(self, name: str) -> None:
        self.profiles = [p for p in self.profiles if p.name != name]
        self.store.save_profiles(self.profiles)
        self.profiles_view.set_profiles(self.profiles)
        self._toast(f"Deleted profile '{name}'.", "info")

    def _export_profile(self, name: str) -> None:
        profile = next((p for p in self.profiles if p.name == name), None)
        if profile is None:
            self._toast("Profile not found.", "error")
            return
        target = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"{name}.profile.json",
            filetypes=[("Profile files", "*.json"), ("All files", "*.*")],
        )
        if not target:
            return
        Path(target).write_text(json.dumps(profile.to_dict(), indent=2), encoding="utf-8")
        self._toast(f"Exported '{name}'.", "success")

    def _import_profile(self) -> None:
        source = filedialog.askopenfilename(
            filetypes=[("Profile files", "*.json"), ("All files", "*.*")]
        )
        if not source:
            return
        try:
            data = json.loads(Path(source).read_text("utf-8"))
            profile = Profile.from_dict(data)
        except Exception as exc:
            self._toast(f"Invalid profile file: {exc}", "error")
            return
        existing = next((p for p in self.profiles if p.name == profile.name), None)
        if existing:
            existing.config = profile.config
        else:
            self.profiles.append(profile)
        self.store.save_profiles(self.profiles)
        self.profiles_view.set_profiles(self.profiles)
        self._toast(f"Imported profile '{profile.name}'.", "success")

    # ---------- macros ----------

    def _toggle_recording(self) -> None:
        if self.recorder.recording:
            macro = self.recorder.stop()
            if macro is not None:
                self._buffered_macro = macro
                self._on_main_thread(lambda: self.macro_view.set_buffer(macro))
                self._toast(
                    f"Recorded {len(macro.events)} events.", "success"
                )
            return
        if not self.recorder.start():
            self._toast("Recording unavailable (missing pyautogui/mouse).", "error")
            return
        self._toast("Recording started — perform actions.", "info")

    def _on_recording_state(self, recording: bool) -> None:
        self._on_main_thread(lambda: self.macro_view.set_recording(recording))

    def _save_buffered_macro(self, name: str) -> None:
        if not self._buffered_macro:
            self._toast("Nothing to save — record something first.", "warning")
            return
        if not name:
            self._toast("Enter a macro name first.", "warning")
            return
        self._buffered_macro.name = name
        save_macro(self._buffered_macro, self.store.macros_dir)
        self.macro_view.set_macros(list_macros(self.store.macros_dir))
        self._buffered_macro = None
        self.macro_view.set_buffer(None)
        self.macro_view.name_var.set("")
        self._toast(f"Saved macro '{name}'.", "success")

    def _play_macro(self, name: str, speed: float, loops: int) -> None:
        if self.player.playing:
            self._stop_playback()
            return
        path = self.store.macros_dir / f"{name}.json"
        try:
            macro = load_macro(path)
        except Exception as exc:
            self._toast(f"Could not load macro: {exc}", "error")
            return
        if self.player.play(macro, speed=speed, loops=loops):
            self.stats.macros_played += 1
            self.store.save_stats(self.stats)
            self.stats_view.update_stats(self.stats)
            self._toast(f"Playing '{name}' at {speed}x × {loops}.", "info")

    def _stop_playback(self) -> None:
        self.player.stop()

    def _on_playback_state(self, playing: bool) -> None:
        self._on_main_thread(lambda: self.macro_view.set_playing(playing))

    def _delete_macro(self, name: str) -> None:
        if delete_macro(name, self.store.macros_dir):
            self.macro_view.set_macros(list_macros(self.store.macros_dir))
            self._toast(f"Deleted '{name}'.", "info")

    def _export_macro(self, name: str) -> None:
        src = self.store.macros_dir / f"{name}.json"
        if not src.exists():
            self._toast("Macro not found.", "error")
            return
        target = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"{name}.json",
            filetypes=[("Macro files", "*.json"), ("All files", "*.*")],
        )
        if not target:
            return
        shutil.copy(src, target)
        self._toast(f"Exported to {Path(target).name}.", "success")

    def _edit_macro(self, name: str) -> None:
        path = self.store.macros_dir / f"{name}.json"
        try:
            macro = load_macro(path)
        except Exception as exc:
            self._toast(f"Could not open macro: {exc}", "error")
            return

        def commit(updated: Macro) -> None:
            updated.name = name
            save_macro(updated, self.store.macros_dir)
            self._toast(f"Saved edits to '{name}'.", "success")

        MacroEditor(self.window, self.palette, macro, on_save=commit)

    def _on_sequence_change(self, steps: list[SequenceStep]) -> None:
        self._sequence = list(steps)
        self.clicker_view.set_sequence(self._sequence)

    def _restore_window(self) -> None:
        try:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
        except Exception:
            pass

    def _quit_app(self) -> None:
        try:
            self._on_close()
        finally:
            try:
                self.window.destroy()
            except Exception:
                pass

    def _import_macro(self) -> None:
        source = filedialog.askopenfilename(
            filetypes=[("Macro files", "*.json"), ("All files", "*.*")]
        )
        if not source:
            return
        src = Path(source)
        try:
            macro = load_macro(src)
        except Exception as exc:
            self._toast(f"Invalid macro file: {exc}", "error")
            return
        macro.name = src.stem
        save_macro(macro, self.store.macros_dir)
        self.macro_view.set_macros(list_macros(self.store.macros_dir))
        self._toast(f"Imported '{macro.name}'.", "success")

    # ---------- settings ----------

    def _on_settings_change(self, settings: AppSettings) -> None:
        old_palette = self.palette
        self.settings = settings
        new_palette = t.palette(settings.theme, settings.accent)
        ctk.set_appearance_mode("dark" if settings.theme == "dark" else "light")
        self.palette = new_palette

        if new_palette != old_palette:
            self.window.update_palette(new_palette)
            self.clicker_view.update_palette(new_palette)
            self.macro_view.update_palette(new_palette)
            self.profiles_view.update_palette(new_palette)
            self.settings_view.update_palette(new_palette)
            self.stats_view.update_palette(new_palette)
            # Force-refresh dynamic content that's color-aware
            self.profiles_view.set_profiles(self.profiles)

        self.hotkeys.apply(settings.hotkeys)
        self.stats_view.update_shortcuts(settings.hotkeys)
        self.store.save_settings(settings)

    # ---------- shared ----------

    def _emergency_stop(self) -> None:
        self.clicker.stop()
        if self.recorder.recording:
            self.recorder.stop()
        self.player.stop()
        self._toast("Emergency stop.", "warning")

    def _on_engine_error(self, msg: str) -> None:
        self._on_main_thread(lambda m=msg: self._toast(m, "error", 5000))

    def _toast(self, msg: str, kind: str = "info", duration_ms: int = 3200) -> None:
        if not self.settings.show_toasts:
            return
        try:
            self.window.toasts.show(msg, kind, duration_ms)
        except Exception:
            pass

    def _on_main_thread(self, fn: Callable[[], None]) -> None:
        try:
            self.window.after(0, fn)
        except Exception:
            pass

    def _on_close(self) -> None:
        try:
            self.clicker.stop()
            if self.recorder.recording:
                self.recorder.stop()
            self.player.stop()
            self.hotkeys.clear()
            self.tray.stop()
        except Exception:
            pass

    def run(self) -> None:
        self.window.mainloop()


def main() -> int:
    app = App()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
