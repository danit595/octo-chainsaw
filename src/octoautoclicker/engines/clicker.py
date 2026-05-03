"""Threaded auto-clicker engine with jitter, fixed/looping repeat, and callbacks."""

from __future__ import annotations

import random
import threading
import time
from typing import Callable, Optional

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover - optional at import time
    pyautogui = None

try:
    import pygetwindow  # type: ignore
except Exception:  # pragma: no cover
    pygetwindow = None

from ..models import ClickConfig, SequenceStep

ClickHook = Callable[[int], None]
StateHook = Callable[[bool], None]
ErrorHook = Callable[[str], None]


class ClickerEngine:
    """Drives the clicking loop on a background thread.

    The engine is callback-driven so the UI can stay decoupled. All callbacks
    are invoked from the worker thread; the UI is responsible for marshalling
    them onto its main loop if needed.
    """

    def __init__(
        self,
        on_click: Optional[ClickHook] = None,
        on_state_change: Optional[StateHook] = None,
        on_error: Optional[ErrorHook] = None,
    ) -> None:
        self._on_click = on_click
        self._on_state_change = on_state_change
        self._on_error = on_error

        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._running = False
        self._count = 0
        self._lock = threading.Lock()

    @property
    def running(self) -> bool:
        return self._running

    @property
    def count(self) -> int:
        return self._count

    def reset_count(self) -> None:
        self._count = 0

    def start(self, config: ClickConfig) -> bool:
        """Start the clicker. Returns False if already running or driver missing."""
        if self._running:
            return False
        if pyautogui is None:
            self._emit_error("pyautogui is not installed; clicking is unavailable.")
            return False

        self._stop.clear()
        self._running = True
        self._thread = threading.Thread(
            target=self._loop, args=(config,), name="clicker-loop", daemon=True
        )
        self._thread.start()
        if self._on_state_change:
            self._on_state_change(True)
        return True

    def stop(self) -> None:
        if not self._running:
            return
        self._stop.set()
        self._running = False
        if self._on_state_change:
            self._on_state_change(False)

    def _loop(self, config: ClickConfig) -> None:
        try:
            base_interval = max(0.001, float(config.interval_seconds))
            jitter_s = max(0, int(config.jitter_ms)) / 1000.0
            jitter_px = max(0, int(config.jitter_pixels))
            max_clicks = (
                int(config.repeat_count) if config.repeat_mode == "fixed_count" else None
            )
            sequence = list(config.sequence) if config.sequence else []
            seq_idx = 0
            target_color = self._parse_color(config.pixel_trigger_color)

            while not self._stop.is_set():
                if not self._target_window_focused(config):
                    if self._stop.wait(0.25):
                        break
                    continue
                if target_color is not None and not self._pixel_matches(
                    config.pixel_trigger_x, config.pixel_trigger_y, target_color
                ):
                    if self._stop.wait(0.05):
                        break
                    continue

                if sequence:
                    step = sequence[seq_idx % len(sequence)]
                    seq_idx += 1
                    if not self._do_step(step, jitter_px):
                        break
                    wait = max(0.001, step.delay_ms / 1000.0)
                else:
                    if not self._do_click(config, jitter_px):
                        break
                    wait = base_interval
                    if jitter_s > 0:
                        wait += random.uniform(-jitter_s, jitter_s)
                    wait = max(0.001, wait)

                with self._lock:
                    self._count += 1
                count = self._count

                if self._on_click:
                    self._on_click(count)

                if max_clicks is not None and count >= max_clicks:
                    break

                if self._stop.wait(wait):
                    break
        finally:
            self._running = False
            if self._on_state_change:
                self._on_state_change(False)

    def _do_step(self, step: SequenceStep, jitter_px: int) -> bool:
        try:
            x, y = int(step.x), int(step.y)
            if jitter_px > 0:
                x += random.randint(-jitter_px, jitter_px)
                y += random.randint(-jitter_px, jitter_px)
            pyautogui.moveTo(x, y, _pause=False)
            if step.click_type == "double":
                pyautogui.doubleClick(button=step.button, _pause=False)
            else:
                pyautogui.click(button=step.button, _pause=False)
            return True
        except getattr(pyautogui, "FailSafeException", Exception):
            self._emit_error("Failsafe triggered. Sequence stopped.")
            return False
        except Exception as exc:
            self._emit_error(f"Sequence step error: {exc}")
            return False

    def _target_window_focused(self, config: ClickConfig) -> bool:
        title = (config.target_window or "").strip().lower()
        if not title or pygetwindow is None:
            return True
        try:
            active = pygetwindow.getActiveWindow()
            if active is None:
                return False
            return title in (active.title or "").lower()
        except Exception:
            return True

    @staticmethod
    def _parse_color(value: str) -> tuple[int, int, int] | None:
        s = (value or "").strip().lstrip("#")
        if len(s) != 6:
            return None
        try:
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        except ValueError:
            return None

    def _pixel_matches(self, x: int, y: int, color: tuple[int, int, int]) -> bool:
        try:
            screenshot = pyautogui.screenshot(region=(int(x), int(y), 1, 1))
            actual = screenshot.getpixel((0, 0))[:3]
            return all(abs(actual[i] - color[i]) <= 8 for i in range(3))
        except Exception:
            return False

    def _do_click(self, config: ClickConfig, jitter_px: int) -> bool:
        try:
            if config.position_mode == "fixed":
                x = int(config.x)
                y = int(config.y)
                if jitter_px > 0:
                    x += random.randint(-jitter_px, jitter_px)
                    y += random.randint(-jitter_px, jitter_px)
                pyautogui.moveTo(x, y, _pause=False)
            elif jitter_px > 0:
                cx, cy = pyautogui.position()
                pyautogui.moveTo(
                    cx + random.randint(-jitter_px, jitter_px),
                    cy + random.randint(-jitter_px, jitter_px),
                    _pause=False,
                )

            if config.click_type == "double":
                pyautogui.doubleClick(button=config.button, _pause=False)
            else:
                pyautogui.click(button=config.button, _pause=False)
            return True
        except getattr(pyautogui, "FailSafeException", Exception) as exc:
            self._emit_error(
                "Failsafe triggered: mouse moved to a screen corner. Clicking stopped."
            )
            return False
        except Exception as exc:
            self._emit_error(f"Click error: {exc}")
            return False

    def _emit_error(self, msg: str) -> None:
        if self._on_error:
            self._on_error(msg)
