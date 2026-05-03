"""Macro recording, library, and playback page."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from ..models import Macro
from . import theme as t
from .widgets import Card, SectionHeader, StatusPill


class MacroView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        palette: dict[str, str],
        on_record_toggle: Callable[[], None],
        on_save: Callable[[str], None],
        on_play: Callable[[str, float, int], None],
        on_stop: Callable[[], None],
        on_delete: Callable[[str], None],
        on_export: Callable[[str], None],
        on_import: Callable[[], None],
        on_edit: Callable[[str], None] | None = None,
    ):
        super().__init__(master, fg_color="transparent")
        self.palette = palette
        self.on_record_toggle = on_record_toggle
        self.on_save = on_save
        self.on_play = on_play
        self.on_stop = on_stop
        self.on_delete = on_delete
        self.on_export = on_export
        self.on_import = on_import
        self.on_edit = on_edit
        self._has_buffer = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_record_card()
        self._build_library_card()

    # ---------- public ----------

    def set_recording(self, recording: bool) -> None:
        if recording:
            self.status_pill.set_state("recording")
            self.record_button.configure(
                text="■  Stop Recording", fg_color=self.palette["danger"]
            )
        else:
            self.status_pill.set_state("idle")
            self.record_button.configure(
                text="●  Start Recording", fg_color=self.palette["primary"]
            )

    def set_playing(self, playing: bool) -> None:
        if playing:
            self.status_pill.set_state("playing")
            self.play_button.configure(
                text="■  Stop Playback", fg_color=self.palette["danger"]
            )
        else:
            self.status_pill.set_state("idle")
            self.play_button.configure(
                text="▶  Play Selected", fg_color=self.palette["primary"]
            )

    def set_buffer(self, macro: Macro | None) -> None:
        self._has_buffer = macro is not None and bool(macro.events)
        if self._has_buffer:
            self.buffer_status.configure(
                text=f"Recorded {len(macro.events)} events ({macro.duration:.1f}s)",
                text_color=self.palette["success"],
            )
            self.save_button.configure(state="normal")
        else:
            self.buffer_status.configure(
                text="No recording in buffer.",
                text_color=self.palette["text_muted"],
            )
            self.save_button.configure(state="disabled")

    def set_macros(self, names: list[str]) -> None:
        self._all_names = list(names)
        self._render_macros()

    def _render_macros(self) -> None:
        query = (self.search_var.get() if hasattr(self, "search_var") else "").strip().lower()
        names = [n for n in getattr(self, "_all_names", []) if not query or query in n.lower()]
        self.macro_listbox.configure(state="normal")
        self.macro_listbox.delete("1.0", "end")
        for name in names:
            self.macro_listbox.insert("end", name + "\n")
        self.macro_listbox.configure(state="disabled")

    def update_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette

    # ---------- layout ----------

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(24, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Macros",
            font=t.FONT_HEADING,
            text_color=self.palette["text"],
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="Record sequences of clicks, moves, and key presses, then play them back.",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
        ).grid(row=1, column=0, sticky="w")

        self.status_pill = StatusPill(header, self.palette)
        self.status_pill.grid(row=0, column=1, rowspan=2, sticky="e")

    def _build_record_card(self) -> None:
        card = Card(self, self.palette)
        card.grid(row=1, column=0, sticky="nsew", padx=(24, 12), pady=(8, 24))
        card.grid_columnconfigure(0, weight=1)

        SectionHeader(
            card,
            self.palette,
            "Record",
            "F7 toggles recording. ESC stops everything.",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 12))

        self.record_button = ctk.CTkButton(
            card,
            text="●  Start Recording",
            command=self.on_record_toggle,
            height=56,
            font=("Segoe UI Variable", 16, "bold"),
            fg_color=self.palette["primary"],
            hover_color=self.palette["primary_hover"],
            text_color="#ffffff",
            corner_radius=12,
        )
        self.record_button.grid(row=1, column=0, sticky="ew", padx=18)

        self.buffer_status = ctk.CTkLabel(
            card,
            text="No recording in buffer.",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
            anchor="w",
        )
        self.buffer_status.grid(row=2, column=0, sticky="ew", padx=18, pady=(12, 6))

        save_row = ctk.CTkFrame(card, fg_color="transparent")
        save_row.grid(row=3, column=0, sticky="ew", padx=18, pady=(6, 18))
        save_row.grid_columnconfigure(0, weight=1)
        self.name_var = ctk.StringVar()
        ctk.CTkEntry(
            save_row,
            textvariable=self.name_var,
            placeholder_text="Name your macro…",
            fg_color=self.palette["surface_alt"],
            border_color=self.palette["border"],
            text_color=self.palette["text"],
            height=40,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.save_button = ctk.CTkButton(
            save_row,
            text="Save",
            command=lambda: self.on_save(self.name_var.get().strip()),
            state="disabled",
            fg_color=self.palette["primary"],
            hover_color=self.palette["primary_hover"],
            text_color="#ffffff",
            height=40,
            corner_radius=10,
        )
        self.save_button.grid(row=0, column=1)

    def _build_library_card(self) -> None:
        card = Card(self, self.palette)
        card.grid(row=1, column=1, sticky="nsew", padx=(12, 24), pady=(8, 24))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        SectionHeader(
            card, self.palette, "Library", "Stored macros, click a name to select."
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 4))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._render_macros())
        ctk.CTkEntry(
            card,
            textvariable=self.search_var,
            placeholder_text="🔍  Filter…",
            fg_color=self.palette["surface_alt"],
            border_color=self.palette["border"],
            text_color=self.palette["text"],
            height=32,
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(4, 8))

        list_wrap = ctk.CTkFrame(
            card,
            fg_color=self.palette["surface_alt"],
            corner_radius=10,
            border_color=self.palette["border"],
            border_width=1,
        )
        list_wrap.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 12))
        list_wrap.grid_columnconfigure(0, weight=1)
        list_wrap.grid_rowconfigure(0, weight=1)

        self.macro_listbox = ctk.CTkTextbox(
            list_wrap,
            fg_color=self.palette["surface_alt"],
            text_color=self.palette["text"],
            border_width=0,
            wrap="none",
        )
        self.macro_listbox.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.macro_listbox.configure(state="disabled")
        self.macro_listbox.bind("<Button-1>", self._on_select_click)
        self.selected_var = ctk.StringVar(value="")

        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 12))
        controls.grid_columnconfigure((0, 1), weight=1)

        self.speed_var = ctk.StringVar(value="1.0")
        self.loops_var = ctk.StringVar(value="1")

        speed_box = ctk.CTkFrame(controls, fg_color="transparent")
        speed_box.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(
            speed_box,
            text="SPEED",
            font=("Segoe UI", 10, "bold"),
            text_color=self.palette["text_muted"],
        ).pack(anchor="w")
        ctk.CTkEntry(
            speed_box,
            textvariable=self.speed_var,
            fg_color=self.palette["surface_alt"],
            border_color=self.palette["border"],
            text_color=self.palette["text"],
        ).pack(fill="x")

        loops_box = ctk.CTkFrame(controls, fg_color="transparent")
        loops_box.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(
            loops_box,
            text="LOOPS",
            font=("Segoe UI", 10, "bold"),
            text_color=self.palette["text_muted"],
        ).pack(anchor="w")
        ctk.CTkEntry(
            loops_box,
            textvariable=self.loops_var,
            fg_color=self.palette["surface_alt"],
            border_color=self.palette["border"],
            text_color=self.palette["text"],
        ).pack(fill="x")

        self.play_button = ctk.CTkButton(
            card,
            text="▶  Play Selected",
            command=self._play,
            height=48,
            font=("Segoe UI Variable", 14, "bold"),
            fg_color=self.palette["primary"],
            hover_color=self.palette["primary_hover"],
            text_color="#ffffff",
            corner_radius=10,
        )
        self.play_button.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 8))

        action_row = ctk.CTkFrame(card, fg_color="transparent")
        action_row.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 18))
        action_row.grid_columnconfigure((0, 1, 2), weight=1)

        action_row.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for col, (label, cmd) in enumerate(
            [
                ("Edit", self._edit),
                ("Delete", self._delete),
                ("Export", self._export),
                ("Import", self.on_import),
            ]
        ):
            ctk.CTkButton(
                action_row,
                text=label,
                command=cmd,
                fg_color="transparent",
                border_color=self.palette["border"],
                border_width=1,
                text_color=self.palette["text"],
                hover_color=self.palette["surface_alt"],
                height=36,
                corner_radius=10,
            ).grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 6, 0))

    # ---------- handlers ----------

    def _on_select_click(self, event) -> None:  # type: ignore[no-untyped-def]
        try:
            index = self.macro_listbox.index(f"@{event.x},{event.y}")
            line_start = index.split(".")[0] + ".0"
            line_end = index.split(".")[0] + ".end"
            self.macro_listbox.tag_remove("sel_row", "1.0", "end")
            self.macro_listbox.tag_add("sel_row", line_start, line_end)
            self.macro_listbox.tag_config(
                "sel_row",
                background=self.palette["primary"],
                foreground="#ffffff",
            )
            text = self.macro_listbox.get(line_start, line_end).strip()
            self.selected_var.set(text)
        except Exception:
            pass

    def _play(self) -> None:
        name = self.selected_var.get()
        if not name:
            return
        try:
            speed = float(self.speed_var.get() or 1.0)
        except ValueError:
            speed = 1.0
        try:
            loops = int(self.loops_var.get() or 1)
        except ValueError:
            loops = 1
        self.on_play(name, speed, loops)

    def _delete(self) -> None:
        name = self.selected_var.get()
        if name:
            self.on_delete(name)

    def _export(self) -> None:
        name = self.selected_var.get()
        if name:
            self.on_export(name)

    def _edit(self) -> None:
        name = self.selected_var.get()
        if name and self.on_edit is not None:
            self.on_edit(name)
