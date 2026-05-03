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

from ..models import ClickConfig

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

            while not self._stop.is_set():
                if not self._do_click(config, jitter_px):
                    break

                with self._lock:
                    self._count += 1
                count = self._count

                if self._on_click:
                    self._on_click(count)

                if max_clicks is not None and count >= max_clicks:
                    break

                wait = base_interval
                if jitter_s > 0:
                    wait += random.uniform(-jitter_s, jitter_s)
                wait = max(0.001, wait)
                if self._stop.wait(wait):
                    break
        finally:
            self._running = False
            if self._on_state_change:
                self._on_state_change(False)

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
