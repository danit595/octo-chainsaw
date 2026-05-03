"""Theme, accent, hotkey, and behavior settings."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from ..config import AppSettings
from ..models import HotkeyConfig
from . import theme as t
from .widgets import Card, SectionHeader


class SettingsView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        palette: dict[str, str],
        settings: AppSettings,
        on_change: Callable[[AppSettings], None],
    ):
        super().__init__(master, fg_color="transparent")
        self.palette = palette
        self.settings = settings
        self.on_change = on_change
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_body()
        self._populate()

    def update_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        ctk.CTkLabel(
            header,
            text="Settings",
            font=t.FONT_HEADING,
            text_color=self.palette["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Personalize the look, hotkeys, and behavior.",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
        ).pack(anchor="w")

    def _build_body(self) -> None:
        wrap = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="nsew", padx=24, pady=(8, 24))
        wrap.grid_columnconfigure(0, weight=1)

        # Appearance card
        appearance = Card(wrap, self.palette)
        appearance.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        appearance.grid_columnconfigure(0, weight=1)
        SectionHeader(
            appearance, self.palette, "Appearance", "Theme and accent color."
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        row = ctk.CTkFrame(appearance, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            row,
            text="THEME",
            font=("Segoe UI", 10, "bold"),
            text_color=self.palette["text_muted"],
        ).grid(row=0, column=0, sticky="w")
        self.theme_var = ctk.StringVar(value=self.settings.theme)
        ctk.CTkSegmentedButton(
            row,
            values=["dark", "light"],
            variable=self.theme_var,
            command=lambda _: self._emit(),
            selected_color=self.palette["primary"],
            selected_hover_color=self.palette["primary_hover"],
        ).grid(row=1, column=0, sticky="ew", pady=(2, 12), padx=(0, 6))

        ctk.CTkLabel(
            row,
            text="ACCENT",
            font=("Segoe UI", 10, "bold"),
            text_color=self.palette["text_muted"],
        ).grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.accent_var = ctk.StringVar(value=self.settings.accent)
        ctk.CTkSegmentedButton(
            row,
            values=["violet", "cyan", "emerald", "rose", "amber"],
            variable=self.accent_var,
            command=lambda _: self._emit(),
            selected_color=self.palette["primary"],
            selected_hover_color=self.palette["primary_hover"],
        ).grid(row=1, column=1, sticky="ew", pady=(2, 12), padx=(6, 0))

        # Hotkeys card
        hotkeys = Card(wrap, self.palette)
        hotkeys.grid(row=1, column=0, sticky="ew", pady=12)
        hotkeys.grid_columnconfigure(0, weight=1)
        SectionHeader(
            hotkeys,
            self.palette,
            "Hotkeys",
            "Use names like 'f6', 'ctrl+shift+a', 'esc'.",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        grid = ctk.CTkFrame(hotkeys, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        grid.grid_columnconfigure(1, weight=1)

        self.hk_vars = {
            "toggle_clicker": ctk.StringVar(value=self.settings.hotkeys.toggle_clicker),
            "toggle_recording": ctk.StringVar(value=self.settings.hotkeys.toggle_recording),
            "toggle_playback": ctk.StringVar(value=self.settings.hotkeys.toggle_playback),
            "emergency_stop": ctk.StringVar(value=self.settings.hotkeys.emergency_stop),
        }
        labels = {
            "toggle_clicker": "Toggle Clicker",
            "toggle_recording": "Toggle Recording",
            "toggle_playback": "Toggle Playback",
            "emergency_stop": "Emergency Stop",
        }
        for i, (key, var) in enumerate(self.hk_vars.items()):
            ctk.CTkLabel(
                grid,
                text=labels[key],
                font=t.FONT_BODY,
                text_color=self.palette["text"],
                anchor="w",
            ).grid(row=i, column=0, sticky="w", pady=4)
            entry = ctk.CTkEntry(
                grid,
                textvariable=var,
                fg_color=self.palette["surface_alt"],
                border_color=self.palette["border"],
                text_color=self.palette["text"],
            )
            entry.grid(row=i, column=1, sticky="ew", padx=(12, 0), pady=4)
            entry.bind("<FocusOut>", lambda _: self._emit())
            entry.bind("<Return>", lambda _: self._emit())

        # Behavior card
        behavior = Card(wrap, self.palette)
        behavior.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        behavior.grid_columnconfigure(0, weight=1)
        SectionHeader(
            behavior, self.palette, "Behavior", "Window and notification preferences."
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        bbox = ctk.CTkFrame(behavior, fg_color="transparent")
        bbox.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        self.minimize_var = ctk.BooleanVar(value=self.settings.minimize_on_start)
        self.toasts_var = ctk.BooleanVar(value=self.settings.show_toasts)
        ctk.CTkCheckBox(
            bbox,
            text="Minimize main window when clicking starts",
            variable=self.minimize_var,
            command=self._emit,
            fg_color=self.palette["primary"],
            hover_color=self.palette["primary_hover"],
            text_color=self.palette["text"],
        ).grid(row=0, column=0, sticky="w", pady=4)
        ctk.CTkCheckBox(
            bbox,
            text="Show toast notifications",
            variable=self.toasts_var,
            command=self._emit,
            fg_color=self.palette["primary"],
            hover_color=self.palette["primary_hover"],
            text_color=self.palette["text"],
        ).grid(row=1, column=0, sticky="w", pady=4)

    def _populate(self) -> None:
        pass  # vars are bound to settings; no extra work needed

    def _emit(self) -> None:
        self.settings.theme = self.theme_var.get()
        self.settings.accent = self.accent_var.get()
        self.settings.minimize_on_start = bool(self.minimize_var.get())
        self.settings.show_toasts = bool(self.toasts_var.get())
        self.settings.hotkeys = HotkeyConfig(
            toggle_clicker=self.hk_vars["toggle_clicker"].get().strip() or "f6",
            toggle_recording=self.hk_vars["toggle_recording"].get().strip() or "f7",
            toggle_playback=self.hk_vars["toggle_playback"].get().strip() or "f8",
            emergency_stop=self.hk_vars["emergency_stop"].get().strip() or "esc",
        )
        self.on_change(self.settings)
