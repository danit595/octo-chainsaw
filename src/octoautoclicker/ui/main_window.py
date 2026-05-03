"""Main window: sidebar nav + view switcher + global toast stack."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

import os
import sys
from pathlib import Path

from .. import __version__
from . import theme as t
from .widgets import SidebarButton, ToastStack


def _icon_path() -> Path | None:
    candidates = []
    base = getattr(sys, "_MEIPASS", None)
    if base:
        candidates.append(Path(base) / "assets" / "octo-icon.ico")
    here = Path(__file__).resolve()
    candidates.append(here.parents[3] / "assets" / "octo-icon.ico")
    candidates.append(here.parents[2] / "assets" / "octo-icon.ico")
    for p in candidates:
        if p.exists():
            return p
    return None


class MainWindow(ctk.CTk):
    """Top-level window with a left sidebar and a right content area."""

    def __init__(self, palette: dict[str, str]):
        super().__init__()
        self.palette = palette
        self.title(f"OctoAutoClicker v{__version__}")
        self.geometry("1080x720")
        self.minsize(960, 640)
        self.configure(fg_color=palette["bg"])
        icon = _icon_path()
        if icon is not None:
            try:
                self.iconbitmap(default=str(icon))
            except Exception:
                pass

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_content_area()
        self.toasts = ToastStack(self, palette)

        self._views: dict[str, ctk.CTkFrame] = {}
        self._buttons: dict[str, SidebarButton] = {}
        self._active: str | None = None
        self._on_quit: Callable[[], None] | None = None
        self.protocol("WM_DELETE_WINDOW", self._handle_close)

    # ---------- public API ----------

    def register_view(
        self, key: str, label: str, icon: str, view: ctk.CTkFrame
    ) -> None:
        self._views[key] = view
        btn = SidebarButton(
            self.sidebar_buttons,
            self.palette,
            label,
            icon,
            command=lambda k=key: self.show(k),
        )
        btn.grid(sticky="ew", pady=2, padx=8)
        self._buttons[key] = btn

    def show(self, key: str) -> None:
        if key not in self._views:
            return
        if self._active and self._active in self._views:
            self._views[self._active].grid_forget()
        if self._active and self._active in self._buttons:
            self._buttons[self._active].set_active(False)
        view = self._views[key]
        view.grid(row=0, column=0, sticky="nsew")
        self._buttons[key].set_active(True)
        self._active = key

    def update_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette
        self.configure(fg_color=palette["bg"])
        self.sidebar.configure(fg_color=palette["surface"], border_color=palette["border"])
        self.brand_dot.configure(text_color=palette["primary"])
        self.brand_label.configure(text_color=palette["text"])
        self.brand_subtitle.configure(text_color=palette["text_muted"])
        self.content.configure(fg_color=palette["bg"])
        self.toasts.update_palette(palette)
        for btn in self._buttons.values():
            btn.palette = palette
            btn.set_active(btn._active)
        self.footer_label.configure(text_color=palette["text_muted"])

    def on_close(self, callback: Callable[[], None]) -> None:
        self._on_quit = callback

    # ---------- layout ----------

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=self.palette["surface"],
            border_color=self.palette["border"],
            border_width=0,
            corner_radius=0,
            width=240,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(1, weight=1)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 16))
        brand.grid_columnconfigure(1, weight=1)

        self.brand_dot = ctk.CTkLabel(
            brand,
            text="◆",
            font=("Segoe UI", 22, "bold"),
            text_color=self.palette["primary"],
            width=28,
        )
        self.brand_dot.grid(row=0, column=0, rowspan=2, sticky="w")
        self.brand_label = ctk.CTkLabel(
            brand,
            text="OctoAutoClicker",
            font=("Segoe UI Variable", 15, "bold"),
            text_color=self.palette["text"],
            anchor="w",
        )
        self.brand_label.grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.brand_subtitle = ctk.CTkLabel(
            brand,
            text=f"v{__version__}",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
            anchor="w",
        )
        self.brand_subtitle.grid(row=1, column=1, sticky="w", padx=(8, 0))

        self.sidebar_buttons = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_buttons.grid(row=1, column=0, sticky="new")
        self.sidebar_buttons.grid_columnconfigure(0, weight=1)

        self.footer_label = ctk.CTkLabel(
            self.sidebar,
            text="F6 · Click   F7 · Record\nF8 · Play   ESC · Stop",
            font=("Segoe UI", 10),
            text_color=self.palette["text_muted"],
            justify="left",
        )
        self.footer_label.grid(row=2, column=0, sticky="sw", padx=20, pady=20)

    def _build_content_area(self) -> None:
        self.content = ctk.CTkFrame(self, fg_color=self.palette["bg"])
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _handle_close(self) -> None:
        if self._on_quit:
            try:
                self._on_quit()
            except Exception:
                pass
        self.destroy()
