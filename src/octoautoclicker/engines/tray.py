"""Optional system-tray icon driven by pystray. No-op when unavailable."""

from __future__ import annotations

import threading
from typing import Callable

try:
    import pystray  # type: ignore
    from pystray import Menu, MenuItem
except Exception:  # pragma: no cover
    pystray = None
    Menu = None
    MenuItem = None

try:
    from PIL import Image, ImageDraw  # type: ignore
except Exception:  # pragma: no cover
    Image = None
    ImageDraw = None


def _build_icon_image(accent: str = "#8B5CF6") -> "Image.Image | None":
    if Image is None:
        return None
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 4, 60, 60), fill=accent)
    d.ellipse((22, 22, 42, 42), fill=(255, 255, 255, 230))
    return img


class TrayIcon:
    def __init__(
        self,
        on_show: Callable[[], None],
        on_toggle_clicker: Callable[[], None],
        on_emergency_stop: Callable[[], None],
        on_quit: Callable[[], None],
        accent: str = "#8B5CF6",
    ) -> None:
        self.on_show = on_show
        self.on_toggle_clicker = on_toggle_clicker
        self.on_emergency_stop = on_emergency_stop
        self.on_quit = on_quit
        self.accent = accent
        self._icon = None
        self._thread: threading.Thread | None = None

    @property
    def available(self) -> bool:
        return pystray is not None and Image is not None

    def start(self) -> bool:
        if not self.available:
            return False
        if self._thread is not None:
            return True
        image = _build_icon_image(self.accent)
        menu = Menu(
            MenuItem("Show OctoAutoClicker", lambda *_: self.on_show(), default=True),
            MenuItem("Toggle Clicker", lambda *_: self.on_toggle_clicker()),
            MenuItem("Emergency Stop", lambda *_: self.on_emergency_stop()),
            Menu.SEPARATOR,
            MenuItem("Quit", lambda *_: self._quit()),
        )
        self._icon = pystray.Icon("OctoAutoClicker", image, "OctoAutoClicker", menu)
        self._thread = threading.Thread(
            target=self._icon.run, name="tray-icon", daemon=True
        )
        self._thread.start()
        return True

    def stop(self) -> None:
        if self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None
        self._thread = None

    def _quit(self) -> None:
        self.stop()
        try:
            self.on_quit()
        except Exception:
            pass
