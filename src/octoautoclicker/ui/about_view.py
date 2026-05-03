"""About / Help page — version, links, dependency credits."""

from __future__ import annotations

import customtkinter as ctk

from .. import __version__
from . import theme as t
from .widgets import Card, SectionHeader


class AboutView(ctk.CTkFrame):
    def __init__(self, master, palette: dict[str, str]):
        super().__init__(master, fg_color="transparent")
        self.palette = palette
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()

    def update_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette

    def _build(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        ctk.CTkLabel(
            header,
            text=f"About OctoAutoClicker",
            font=t.FONT_HEADING,
            text_color=self.palette["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text=f"Version {__version__}  ·  MIT License",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
        ).pack(anchor="w")

        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(8, 24))
        body.grid_columnconfigure(0, weight=1)

        intro = Card(body, self.palette)
        intro.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        intro.grid_columnconfigure(0, weight=1)
        SectionHeader(intro, self.palette, "What it does").grid(
            row=0, column=0, sticky="ew", padx=18, pady=(16, 6)
        )
        ctk.CTkLabel(
            intro,
            text=(
                "A modern Windows auto-clicker and macro recorder.\n"
                "Configurable timing and position jitter. Reorderable click sequences.\n"
                "Optional active-window and pixel-color triggers.\n"
                "Macro recording with editable events, speed, and loops."
            ),
            font=t.FONT_BODY,
            text_color=self.palette["text"],
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))

        tips = Card(body, self.palette)
        tips.grid(row=1, column=0, sticky="ew", pady=12)
        tips.grid_columnconfigure(0, weight=1)
        SectionHeader(tips, self.palette, "Tips").grid(
            row=0, column=0, sticky="ew", padx=18, pady=(16, 6)
        )
        ctk.CTkLabel(
            tips,
            text=(
                "• Move the mouse to any screen corner to instantly stop (PyAutoGUI failsafe).\n"
                "• Press the configured emergency-stop key (default ESC) any time.\n"
                "• A non-empty Sequence overrides single-click mode.\n"
                "• Set TARGET WINDOW to a substring like 'notepad' to gate clicks by focus.\n"
                "• Use the Mini view from the sidebar for an always-on-top compact controller."
            ),
            font=t.FONT_BODY,
            text_color=self.palette["text"],
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))

        credits = Card(body, self.palette)
        credits.grid(row=2, column=0, sticky="ew", pady=12)
        credits.grid_columnconfigure(0, weight=1)
        SectionHeader(credits, self.palette, "Built with").grid(
            row=0, column=0, sticky="ew", padx=18, pady=(16, 6)
        )
        ctk.CTkLabel(
            credits,
            text=(
                "CustomTkinter · PyAutoGUI · keyboard · mouse · pygetwindow ·\n"
                "Pillow · pystray · PyInstaller"
            ),
            font=t.FONT_MONO,
            text_color=self.palette["text_muted"],
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
