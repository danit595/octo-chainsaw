"""Wraps the `keyboard` library to manage user-customizable global hotkeys."""

from __future__ import annotations

from typing import Callable

try:
    import keyboard  # type: ignore
except Exception:  # pragma: no cover
    keyboard = None

from ..models import HotkeyConfig


class HotkeyManager:
    """Registers and re-registers global hotkey handlers."""

    def __init__(self) -> None:
        self._handlers: list = []
        self._actions: dict[str, Callable[[], None]] = {}

    def bind(self, name: str, action: Callable[[], None]) -> None:
        self._actions[name] = action

    def apply(self, config: HotkeyConfig) -> bool:
        """Clear existing hotkeys and rebind from config. Returns success."""
        self.clear()
        if keyboard is None:
            return False
        mapping = {
            "toggle_clicker": config.toggle_clicker,
            "toggle_recording": config.toggle_recording,
            "toggle_playback": config.toggle_playback,
            "emergency_stop": config.emergency_stop,
        }
        ok = True
        for action_name, key in mapping.items():
            handler = self._actions.get(action_name)
            if not handler or not key:
                continue
            try:
                self._handlers.append(
                    keyboard.add_hotkey(key, handler, suppress=False, trigger_on_release=False)
                )
            except Exception:
                ok = False
        return ok

    def clear(self) -> None:
        if keyboard is None:
            self._handlers.clear()
            return
        for h in self._handlers:
            try:
                keyboard.remove_hotkey(h)
            except Exception:
                pass
        self._handlers.clear()
