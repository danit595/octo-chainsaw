"""Compact always-on-top window with start/stop + live status."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from . import theme as t


class MiniController(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        palette: dict[str, str],
        on_toggle: Callable[[], None],
        on_emergency_stop: Callable[[], None],
        on_open_main: Callable[[], None],
    ):
        super().__init__(master)
        self.palette = palette
        self.on_toggle = on_toggle
        self.on_emergency_stop = on_emergency_stop
        self.on_open_main = on_open_main

        self.title("OctoAutoClicker — mini")
        self.geometry("280x108")
        self.minsize(260, 100)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=palette["surface"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.status_dot = ctk.CTkLabel(
            self,
            text="●",
            font=("Segoe UI", 22),
            text_color=palette["text_muted"],
            width=24,
        )
        self.status_dot.grid(row=0, column=0, padx=(14, 8))

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=0, column=1, sticky="nsew", pady=14)
        center.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(
            center,
            text="Idle",
            font=("Segoe UI Variable", 14, "bold"),
            text_color=palette["text"],
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        self.cps_label = ctk.CTkLabel(
            center,
            text="0.0 CPS  ·  0 clicks",
            font=("Segoe UI", 11),
            text_color=palette["text_muted"],
            anchor="w",
        )
        self.cps_label.grid(row=1, column=0, sticky="w")

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=2, padx=10)
        self.toggle_button = ctk.CTkButton(
            actions,
            text="▶",
            width=42,
            height=42,
            font=("Segoe UI", 14, "bold"),
            corner_radius=10,
            fg_color=palette["primary"],
            hover_color=palette["primary_hover"],
            text_color="#ffffff",
            command=on_toggle,
        )
        self.toggle_button.grid(row=0, column=0, padx=2)
        ctk.CTkButton(
            actions,
            text="⛶",
            width=32,
            height=42,
            corner_radius=10,
            font=("Segoe UI", 12),
            fg_color="transparent",
            border_color=palette["border"],
            border_width=1,
            text_color=palette["text"],
            hover_color=palette["surface_alt"],
            command=on_open_main,
        ).grid(row=0, column=1, padx=2)

        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def set_running(self, running: bool) -> None:
        if running:
            self.status_label.configure(text="Clicking", text_color=self.palette["success"])
            self.status_dot.configure(text_color=self.palette["success"])
            self.toggle_button.configure(text="■", fg_color=self.palette["danger"])
        else:
            self.status_label.configure(text="Idle", text_color=self.palette["text"])
            self.status_dot.configure(text_color=self.palette["text_muted"])
            self.toggle_button.configure(text="▶", fg_color=self.palette["primary"])

    def update_metrics(self, cps: float, total: int) -> None:
        self.cps_label.configure(text=f"{cps:.1f} CPS  ·  {total:,} clicks")
