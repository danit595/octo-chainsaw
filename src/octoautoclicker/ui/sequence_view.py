"""Click sequence editor — multi-target click queue."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from ..models import SequenceStep
from . import theme as t
from .widgets import Card, SectionHeader


class SequenceView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        palette: dict[str, str],
        on_change: Callable[[list[SequenceStep]], None],
        on_pick_position: Callable[[Callable[[int, int], None]], None],
    ):
        super().__init__(master, fg_color="transparent")
        self.palette = palette
        self.on_change = on_change
        self.on_pick_position = on_pick_position
        self._steps: list[SequenceStep] = []
        self._row_widgets: list[ctk.CTkFrame] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build_header()
        self._build_actions()
        self._build_list()

    def update_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette

    def set_steps(self, steps: list[SequenceStep]) -> None:
        self._steps = list(steps)
        self._render()

    # ---------- layout ----------

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        ctk.CTkLabel(
            header,
            text="Click Sequence",
            font=t.FONT_HEADING,
            text_color=self.palette["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Define a queue of points to click in order. The sequence runs "
            "instead of single-position clicking when it has at least one step.",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
            justify="left",
            wraplength=700,
        ).pack(anchor="w")

    def _build_actions(self) -> None:
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        ctk.CTkButton(
            actions,
            text="＋  Add step",
            command=self._add_step,
            fg_color=self.palette["primary"],
            hover_color=self.palette["primary_hover"],
            text_color="#ffffff",
            corner_radius=10,
            height=36,
        ).pack(side="left")
        ctk.CTkButton(
            actions,
            text="🎯  Pick & add",
            command=self._pick_and_add,
            fg_color="transparent",
            border_color=self.palette["border"],
            border_width=1,
            text_color=self.palette["text"],
            hover_color=self.palette["surface_alt"],
            corner_radius=10,
            height=36,
        ).pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            actions,
            text="🗑  Clear",
            command=self._clear,
            fg_color="transparent",
            border_color=self.palette["border"],
            border_width=1,
            text_color=self.palette["text"],
            hover_color=self.palette["surface_alt"],
            corner_radius=10,
            height=36,
        ).pack(side="left", padx=(8, 0))

    def _build_list(self) -> None:
        wrap = Card(self, self.palette)
        wrap.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        wrap.grid_rowconfigure(1, weight=1)
        wrap.grid_columnconfigure(0, weight=1)
        SectionHeader(wrap, self.palette, "Steps").grid(
            row=0, column=0, sticky="ew", padx=18, pady=(16, 4)
        )
        self.list_frame = ctk.CTkScrollableFrame(wrap, fg_color="transparent")
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))
        self.list_frame.grid_columnconfigure(0, weight=1)
        self._render()

    # ---------- rendering ----------

    def _render(self) -> None:
        for w in self._row_widgets:
            w.destroy()
        self._row_widgets.clear()

        if not self._steps:
            empty = ctk.CTkLabel(
                self.list_frame,
                text="No steps yet — add one to start a sequence.",
                font=t.FONT_MUTED,
                text_color=self.palette["text_muted"],
            )
            empty.grid(row=0, column=0, pady=24)
            self._row_widgets.append(empty)
            return

        for idx, step in enumerate(self._steps):
            row = self._build_row(idx, step)
            row.grid(row=idx, column=0, sticky="ew", padx=8, pady=4)
            self._row_widgets.append(row)

    def _build_row(self, idx: int, step: SequenceStep) -> ctk.CTkFrame:
        row = ctk.CTkFrame(
            self.list_frame,
            fg_color=self.palette["surface_alt"],
            corner_radius=10,
            border_color=self.palette["border"],
            border_width=1,
        )
        row.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            row,
            text=f"{idx + 1:02d}",
            font=("Segoe UI Variable", 14, "bold"),
            text_color=self.palette["primary"],
            width=30,
        ).grid(row=0, column=0, padx=(12, 6), pady=10)

        x_var = ctk.StringVar(value=str(step.x))
        y_var = ctk.StringVar(value=str(step.y))
        button_var = ctk.StringVar(value=step.button)
        ct_var = ctk.StringVar(value=step.click_type)
        delay_var = ctk.StringVar(value=str(step.delay_ms))

        coords = ctk.CTkFrame(row, fg_color="transparent")
        coords.grid(row=0, column=1, padx=4, pady=8)
        ctk.CTkEntry(
            coords, textvariable=x_var, width=64,
            fg_color=self.palette["surface"], border_color=self.palette["border"],
            text_color=self.palette["text"],
        ).grid(row=0, column=0, padx=2)
        ctk.CTkEntry(
            coords, textvariable=y_var, width=64,
            fg_color=self.palette["surface"], border_color=self.palette["border"],
            text_color=self.palette["text"],
        ).grid(row=0, column=1, padx=2)

        ctk.CTkSegmentedButton(
            row, values=["left", "right", "middle"], variable=button_var,
            selected_color=self.palette["primary"],
            selected_hover_color=self.palette["primary_hover"],
        ).grid(row=0, column=2, padx=4, sticky="ew")

        ctk.CTkSegmentedButton(
            row, values=["single", "double"], variable=ct_var,
            selected_color=self.palette["primary"],
            selected_hover_color=self.palette["primary_hover"],
        ).grid(row=0, column=3, padx=4)

        ctk.CTkEntry(
            row, textvariable=delay_var, width=72,
            fg_color=self.palette["surface"], border_color=self.palette["border"],
            text_color=self.palette["text"],
        ).grid(row=0, column=4, padx=4)

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=5, padx=(4, 8))
        ctk.CTkButton(
            actions, text="↑", width=28, height=28, corner_radius=6,
            fg_color="transparent", hover_color=self.palette["border"],
            text_color=self.palette["text"],
            command=lambda i=idx: self._move(i, -1),
        ).grid(row=0, column=0, padx=1)
        ctk.CTkButton(
            actions, text="↓", width=28, height=28, corner_radius=6,
            fg_color="transparent", hover_color=self.palette["border"],
            text_color=self.palette["text"],
            command=lambda i=idx: self._move(i, +1),
        ).grid(row=0, column=1, padx=1)
        ctk.CTkButton(
            actions, text="✕", width=28, height=28, corner_radius=6,
            fg_color="transparent", hover_color=self.palette["danger"],
            text_color=self.palette["danger"],
            command=lambda i=idx: self._remove(i),
        ).grid(row=0, column=2, padx=1)

        def commit(_=None, i=idx, xv=x_var, yv=y_var, bv=button_var, cv=ct_var, dv=delay_var):
            try:
                self._steps[i] = SequenceStep(
                    x=int(xv.get() or 0),
                    y=int(yv.get() or 0),
                    button=bv.get(),  # type: ignore[arg-type]
                    click_type=cv.get(),  # type: ignore[arg-type]
                    delay_ms=int(dv.get() or 100),
                )
                self.on_change(self._steps)
            except ValueError:
                pass

        for var in (x_var, y_var, button_var, ct_var, delay_var):
            var.trace_add("write", lambda *_a, _f=commit: _f())
        return row

    # ---------- actions ----------

    def _add_step(self) -> None:
        self._steps.append(SequenceStep(x=0, y=0))
        self._render()
        self.on_change(self._steps)

    def _pick_and_add(self) -> None:
        def receive(x: int, y: int) -> None:
            self._steps.append(SequenceStep(x=x, y=y))
            self._render()
            self.on_change(self._steps)

        self.on_pick_position(receive)

    def _clear(self) -> None:
        self._steps.clear()
        self._render()
        self.on_change(self._steps)

    def _move(self, idx: int, direction: int) -> None:
        target = idx + direction
        if 0 <= target < len(self._steps):
            self._steps[idx], self._steps[target] = self._steps[target], self._steps[idx]
            self._render()
            self.on_change(self._steps)

    def _remove(self, idx: int) -> None:
        if 0 <= idx < len(self._steps):
            self._steps.pop(idx)
            self._render()
            self.on_change(self._steps)
