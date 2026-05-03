"""Lifetime stats and shortcut cheatsheet."""

from __future__ import annotations

import customtkinter as ctk

from ..models import HotkeyConfig, Stats
from . import theme as t
from .widgets import Card, SectionHeader, StatTile


class StatsView(ctk.CTkFrame):
    def __init__(self, master, palette: dict[str, str]):
        super().__init__(master, fg_color="transparent")
        self.palette = palette
        self.grid_columnconfigure(0, weight=1)
        self._build_header()
        self._build_tiles()
        self._build_shortcuts()

    def update_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette

    def update_stats(self, stats: Stats) -> None:
        self.tiles["clicks"].set_value(f"{stats.total_clicks:,}")
        self.tiles["sessions"].set_value(f"{stats.total_sessions:,}")
        mins = stats.total_seconds_active / 60.0
        self.tiles["active"].set_value(f"{mins:,.1f}m")
        self.tiles["macros"].set_value(f"{stats.macros_played:,}")

    def update_shortcuts(self, hotkeys: HotkeyConfig) -> None:
        self.shortcuts.configure(
            text=(
                f"Toggle Clicker:    {hotkeys.toggle_clicker.upper()}\n"
                f"Toggle Recording:  {hotkeys.toggle_recording.upper()}\n"
                f"Toggle Playback:   {hotkeys.toggle_playback.upper()}\n"
                f"Emergency Stop:    {hotkeys.emergency_stop.upper()}\n"
                f"PyAutoGUI Failsafe: move mouse to any screen corner"
            )
        )

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        ctk.CTkLabel(
            header,
            text="Stats & Shortcuts",
            font=t.FONT_HEADING,
            text_color=self.palette["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Lifetime usage and quick reference for hotkeys.",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
        ).pack(anchor="w")

    def _build_tiles(self) -> None:
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="ew", padx=24, pady=(8, 12))
        wrap.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.tiles = {
            "clicks": StatTile(wrap, self.palette, "Lifetime clicks"),
            "sessions": StatTile(wrap, self.palette, "Sessions"),
            "active": StatTile(wrap, self.palette, "Active time"),
            "macros": StatTile(wrap, self.palette, "Macros played"),
        }
        for col, key in enumerate(("clicks", "sessions", "active", "macros")):
            self.tiles[key].grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 6, 6 if col != 3 else 0))

    def _build_shortcuts(self) -> None:
        card = Card(self, self.palette)
        card.grid(row=2, column=0, sticky="ew", padx=24, pady=(12, 24))
        card.grid_columnconfigure(0, weight=1)
        SectionHeader(card, self.palette, "Shortcuts", "Global hotkeys.").grid(
            row=0, column=0, sticky="ew", padx=18, pady=(16, 8)
        )
        self.shortcuts = ctk.CTkLabel(
            card,
            text="",
            font=t.FONT_MONO,
            text_color=self.palette["text"],
            justify="left",
            anchor="w",
        )
        self.shortcuts.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 18))
