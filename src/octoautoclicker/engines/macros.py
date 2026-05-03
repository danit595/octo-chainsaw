"""Macro recording, persistence, and playback engine."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Callable, Optional

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None

try:
    import mouse  # type: ignore
except Exception:  # pragma: no cover
    mouse = None

try:
    import keyboard  # type: ignore
except Exception:  # pragma: no cover
    keyboard = None

from ..models import Macro, MacroEvent

ProgressHook = Callable[[int, int], None]
StateHook = Callable[[bool], None]
ErrorHook = Callable[[str], None]


class MacroRecorder:
    """Records mouse moves, clicks, and key events on a background thread."""

    def __init__(
        self,
        on_state_change: Optional[StateHook] = None,
        capture_keyboard: bool = True,
    ) -> None:
        self._on_state_change = on_state_change
        self._capture_keyboard = capture_keyboard
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._recording = False
        self._events: list[MacroEvent] = []
        self._kb_handler = None

    @property
    def recording(self) -> bool:
        return self._recording

    @property
    def events(self) -> list[MacroEvent]:
        return list(self._events)

    def start(self) -> bool:
        if self._recording:
            return False
        if pyautogui is None or mouse is None:
            return False
        self._events = []
        self._stop.clear()
        self._recording = True
        if self._capture_keyboard and keyboard is not None:
            start_time = time.time()
            self._kb_start = start_time

            def _kb(event):  # type: ignore[no-untyped-def]
                if not self._recording:
                    return
                self._events.append(
                    MacroEvent(
                        type="key",
                        time=time.time() - self._kb_start,
                        key=event.name,
                        pressed=event.event_type == "down",
                    )
                )

            try:
                self._kb_handler = keyboard.hook(_kb)
            except Exception:
                self._kb_handler = None

        self._thread = threading.Thread(
            target=self._loop, name="macro-recorder", daemon=True
        )
        self._thread.start()
        if self._on_state_change:
            self._on_state_change(True)
        return True

    def stop(self) -> Macro | None:
        if not self._recording:
            return None
        self._stop.set()
        self._recording = False
        if self._kb_handler is not None and keyboard is not None:
            try:
                keyboard.unhook(self._kb_handler)
            except Exception:
                pass
            self._kb_handler = None
        if self._on_state_change:
            self._on_state_change(False)
        return Macro(name="recorded", events=self.events)

    def _loop(self) -> None:
        start = time.time()
        last_pos = pyautogui.position()
        last_click_state = {b: False for b in ("left", "right", "middle")}
        try:
            while not self._stop.is_set():
                now = time.time() - start
                pos = pyautogui.position()
                if pos != last_pos:
                    self._events.append(
                        MacroEvent(type="move", time=now, x=int(pos[0]), y=int(pos[1]))
                    )
                    last_pos = pos
                for btn in ("left", "right", "middle"):
                    pressed = mouse.is_pressed(button=btn)
                    if pressed and not last_click_state[btn]:
                        self._events.append(
                            MacroEvent(
                                type="click",
                                time=now,
                                button=btn,  # type: ignore[arg-type]
                                pressed=True,
                                x=int(pos[0]),
                                y=int(pos[1]),
                            )
                        )
                    last_click_state[btn] = pressed
                self._stop.wait(0.01)
        except Exception:
            pass


class MacroPlayer:
    """Plays back a recorded macro with optional speed and loop count."""

    def __init__(
        self,
        on_state_change: Optional[StateHook] = None,
        on_progress: Optional[ProgressHook] = None,
        on_error: Optional[ErrorHook] = None,
    ) -> None:
        self._on_state_change = on_state_change
        self._on_progress = on_progress
        self._on_error = on_error
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._playing = False

    @property
    def playing(self) -> bool:
        return self._playing

    def play(self, macro: Macro, speed: float = 1.0, loops: int = 1) -> bool:
        if self._playing:
            return False
        if pyautogui is None:
            if self._on_error:
                self._on_error("pyautogui not installed; playback unavailable.")
            return False
        if not macro.events:
            if self._on_error:
                self._on_error("Macro has no events to play.")
            return False

        self._stop.clear()
        self._playing = True
        self._thread = threading.Thread(
            target=self._loop,
            args=(macro, max(0.1, float(speed)), max(1, int(loops))),
            name="macro-player",
            daemon=True,
        )
        self._thread.start()
        if self._on_state_change:
            self._on_state_change(True)
        return True

    def stop(self) -> None:
        if not self._playing:
            return
        self._stop.set()

    def _loop(self, macro: Macro, speed: float, loops: int) -> None:
        try:
            total = len(macro.events)
            for _loop_idx in range(loops):
                if self._stop.is_set():
                    break
                last_t = 0.0
                for idx, event in enumerate(macro.events, start=1):
                    if self._stop.is_set():
                        break
                    delay = (event.time - last_t) / speed
                    if delay > 0 and self._stop.wait(delay):
                        break
                    self._dispatch(event)
                    last_t = event.time
                    if self._on_progress:
                        self._on_progress(idx, total)
        except Exception as exc:
            if self._on_error:
                self._on_error(f"Playback error: {exc}")
        finally:
            self._playing = False
            if self._on_state_change:
                self._on_state_change(False)

    def _dispatch(self, event: MacroEvent) -> None:
        if event.type == "move" and event.x is not None and event.y is not None:
            pyautogui.moveTo(event.x, event.y, _pause=False)
        elif event.type == "click" and event.button:
            pyautogui.click(button=event.button, _pause=False)
        elif event.type == "key" and event.key and keyboard is not None:
            try:
                if event.pressed:
                    keyboard.press(event.key)
                else:
                    keyboard.release(event.key)
            except Exception:
                pass


def save_macro(macro: Macro, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{macro.name}.json"
    path.write_text(json.dumps(macro.to_dict(), indent=2), encoding="utf-8")
    return path


def load_macro(path: Path) -> Macro:
    data = json.loads(path.read_text("utf-8"))
    if "name" not in data:
        data["name"] = path.stem
    return Macro.from_dict(data)


def list_macros(directory: Path) -> list[str]:
    if not directory.exists():
        return []
    return sorted(p.stem for p in directory.glob("*.json"))


def delete_macro(name: str, directory: Path) -> bool:
    path = directory / f"{name}.json"
    if not path.exists():
        return False
    path.unlink()
    return True
