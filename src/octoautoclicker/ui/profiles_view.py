"""Saved click profiles."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from ..models import Profile
from . import theme as t
from .widgets import Card, SectionHeader


class ProfilesView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        palette: dict[str, str],
        on_apply: Callable[[Profile], None],
        on_delete: Callable[[str], None],
        on_export: Callable[[str], None] | None = None,
        on_import: Callable[[], None] | None = None,
    ):
        super().__init__(master, fg_color="transparent")
        self.palette = palette
        self.on_apply = on_apply
        self.on_delete = on_delete
        self.on_export = on_export
        self.on_import = on_import
        self._profiles: list[Profile] = []
        self._cards: list[ctk.CTkFrame] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_grid()

    def update_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette

    def set_profiles(self, profiles: list[Profile]) -> None:
        self._profiles = profiles
        for card in self._cards:
            card.destroy()
        self._cards.clear()

        for idx, profile in enumerate(profiles):
            card = self._build_profile_card(profile)
            row, col = divmod(idx, 2)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            self._cards.append(card)

        self.grid_container.grid_columnconfigure((0, 1), weight=1)
        if not profiles:
            self.empty_label.grid(row=0, column=0, sticky="nsew", pady=40)
        else:
            self.empty_label.grid_forget()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        header.grid_columnconfigure(0, weight=1)
        text_box = ctk.CTkFrame(header, fg_color="transparent")
        text_box.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            text_box,
            text="Profiles",
            font=t.FONT_HEADING,
            text_color=self.palette["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_box,
            text="Save and re-apply common clicker configurations.",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
        ).pack(anchor="w")

        if self.on_import is not None or self.on_export is not None:
            actions = ctk.CTkFrame(header, fg_color="transparent")
            actions.grid(row=0, column=1, sticky="e")
            if self.on_import is not None:
                ctk.CTkButton(
                    actions,
                    text="Import",
                    command=self.on_import,
                    fg_color="transparent",
                    border_color=self.palette["border"],
                    border_width=1,
                    text_color=self.palette["text"],
                    hover_color=self.palette["surface_alt"],
                    height=34,
                    corner_radius=10,
                ).grid(row=0, column=0, padx=(0, 8))

    def _build_grid(self) -> None:
        wrap = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 24))
        wrap.grid_columnconfigure((0, 1), weight=1)
        self.grid_container = wrap
        self.empty_label = ctk.CTkLabel(
            wrap,
            text="No profiles yet — save one from the Auto Clicker tab.",
            font=t.FONT_BODY,
            text_color=self.palette["text_muted"],
        )

    def _build_profile_card(self, profile: Profile) -> ctk.CTkFrame:
        card = Card(self.grid_container, self.palette)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=profile.name,
            font=t.FONT_SUBHEADING,
            text_color=self.palette["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))

        cfg = profile.config
        summary = (
            f"{cfg.button.title()} · {cfg.click_type.title()}\n"
            f"Every {cfg.interval_seconds*1000:.0f} ms"
            f"{f' (±{cfg.jitter_ms}ms)' if cfg.jitter_ms else ''}\n"
            f"{cfg.position_mode.title()} position"
            f"{f' ({cfg.x}, {cfg.y})' if cfg.position_mode == 'fixed' else ''}"
        )
        ctk.CTkLabel(
            card,
            text=summary,
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(2, 12))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        actions.grid_columnconfigure((0, 1), weight=1)

        actions.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(
            actions,
            text="Apply",
            command=lambda p=profile: self.on_apply(p),
            fg_color=self.palette["primary"],
            hover_color=self.palette["primary_hover"],
            text_color="#ffffff",
            height=34,
            corner_radius=8,
        ).grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkButton(
            actions,
            text="Export",
            command=lambda n=profile.name: self.on_export(n) if self.on_export else None,
            fg_color="transparent",
            border_color=self.palette["border"],
            border_width=1,
            text_color=self.palette["text"],
            hover_color=self.palette["surface_alt"],
            height=34,
            corner_radius=8,
        ).grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkButton(
            actions,
            text="Delete",
            command=lambda n=profile.name: self.on_delete(n),
            fg_color="transparent",
            border_color=self.palette["border"],
            border_width=1,
            text_color=self.palette["text"],
            hover_color=self.palette["surface_alt"],
            height=34,
            corner_radius=8,
        ).grid(row=0, column=2, sticky="ew", padx=4)
        return card
