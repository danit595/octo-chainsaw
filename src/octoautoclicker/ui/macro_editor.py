"""Modal-style page that edits the events of a saved macro."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from ..models import Macro, MacroEvent
from . import theme as t
from .widgets import Card, SectionHeader


class MacroEditor(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        palette: dict[str, str],
        macro: Macro,
        on_save: Callable[[Macro], None],
    ):
        super().__init__(master)
        self.title(f"Edit macro — {macro.name}")
        self.geometry("780x560")
        self.configure(fg_color=palette["bg"])
        self.palette = palette
        self.macro = Macro(name=macro.name, events=list(macro.events))
        self.on_save = on_save
        self._row_widgets: list[ctk.CTkFrame] = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text=f"Editing: {macro.name}",
            font=t.FONT_HEADING,
            text_color=palette["text"],
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text=f"{len(macro.events)} events · {macro.duration:.2f}s",
            font=t.FONT_MUTED,
            text_color=palette["text_muted"],
        ).grid(row=1, column=0, sticky="w")

        body = Card(self, palette)
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 12))
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)
        SectionHeader(body, palette, "Events").grid(
            row=0, column=0, sticky="ew", padx=14, pady=(14, 4)
        )
        self.list_frame = ctk.CTkScrollableFrame(body, fg_color="transparent")
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))
        self.list_frame.grid_columnconfigure(0, weight=1)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        footer.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(
            footer,
            text="Cancel",
            command=self.destroy,
            fg_color="transparent",
            border_color=palette["border"],
            border_width=1,
            text_color=palette["text"],
            hover_color=palette["surface_alt"],
            corner_radius=10,
            height=40,
        ).grid(row=0, column=1, padx=(0, 8))
        ctk.CTkButton(
            footer,
            text="Save",
            command=self._save,
            fg_color=palette["primary"],
            hover_color=palette["primary_hover"],
            text_color="#ffffff",
            corner_radius=10,
            height=40,
        ).grid(row=0, column=2)

        self._render()
        self.transient(master)
        self.lift()
        self.focus()

    def _render(self) -> None:
        for w in self._row_widgets:
            w.destroy()
        self._row_widgets.clear()

        if not self.macro.events:
            lbl = ctk.CTkLabel(
                self.list_frame,
                text="Macro has no events.",
                font=t.FONT_MUTED,
                text_color=self.palette["text_muted"],
            )
            lbl.grid(row=0, column=0, pady=24)
            self._row_widgets.append(lbl)
            return

        for idx, event in enumerate(self.macro.events):
            row = self._build_row(idx, event)
            row.grid(row=idx, column=0, sticky="ew", padx=8, pady=2)
            self._row_widgets.append(row)

    def _build_row(self, idx: int, event: MacroEvent) -> ctk.CTkFrame:
        row = ctk.CTkFrame(
            self.list_frame,
            fg_color=self.palette["surface_alt"],
            corner_radius=8,
            border_color=self.palette["border"],
            border_width=1,
        )
        row.grid_columnconfigure(3, weight=1)

        type_color = {
            "move": self.palette["text_muted"],
            "click": self.palette["primary"],
            "key": self.palette["success"],
        }.get(event.type, self.palette["text"])

        ctk.CTkLabel(
            row,
            text=f"{idx + 1:03d}",
            font=("JetBrains Mono", 11),
            text_color=self.palette["text_muted"],
            width=40,
        ).grid(row=0, column=0, padx=(10, 4), pady=8)
        ctk.CTkLabel(
            row,
            text=event.type.upper(),
            font=("Segoe UI", 10, "bold"),
            text_color=type_color,
            width=60,
        ).grid(row=0, column=1, padx=4)

        time_var = ctk.StringVar(value=f"{event.time:.3f}")
        ctk.CTkEntry(
            row, textvariable=time_var, width=80,
            fg_color=self.palette["surface"], border_color=self.palette["border"],
            text_color=self.palette["text"],
        ).grid(row=0, column=2, padx=4)

        detail_text = []
        if event.x is not None and event.y is not None:
            detail_text.append(f"({event.x}, {event.y})")
        if event.button:
            detail_text.append(event.button)
        if event.key:
            detail_text.append(f"key:{event.key}")
        if event.pressed is not None:
            detail_text.append("down" if event.pressed else "up")
        ctk.CTkLabel(
            row,
            text="  ·  ".join(detail_text) or "—",
            font=("Segoe UI", 11),
            text_color=self.palette["text"],
            anchor="w",
        ).grid(row=0, column=3, padx=8, sticky="ew")

        ctk.CTkButton(
            row, text="✕", width=28, height=28, corner_radius=6,
            fg_color="transparent", hover_color=self.palette["danger"],
            text_color=self.palette["danger"],
            command=lambda i=idx: self._remove(i),
        ).grid(row=0, column=4, padx=(4, 8))

        def commit(_=None, i=idx, tv=time_var):
            try:
                self.macro.events[i].time = float(tv.get())
            except ValueError:
                pass

        time_var.trace_add("write", lambda *_a: commit())
        return row

    def _remove(self, idx: int) -> None:
        if 0 <= idx < len(self.macro.events):
            self.macro.events.pop(idx)
            self._render()

    def _save(self) -> None:
        self.macro.events.sort(key=lambda e: e.time)
        self.on_save(self.macro)
        self.destroy()
