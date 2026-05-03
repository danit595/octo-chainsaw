"""Auto-clicker page: configuration cards + big start button + live stats."""

from __future__ import annotations

import time
from typing import Callable

import customtkinter as ctk

from ..models import ClickConfig
from . import theme as t
from .widgets import Card, LabeledEntry, SectionHeader, StatTile, StatusPill


class ClickerView(ctk.CTkFrame):
    """The main auto-clicker tab."""

    def __init__(
        self,
        master,
        palette: dict[str, str],
        on_start_stop: Callable[[ClickConfig | None], None],
        on_pick_position: Callable[[Callable[[int, int], None]], None],
        on_save_profile: Callable[[ClickConfig], None],
    ):
        super().__init__(master, fg_color="transparent")
        self.palette = palette
        self.on_start_stop = on_start_stop
        self.on_pick_position = on_pick_position
        self.on_save_profile = on_save_profile
        self._cps_window: list[float] = []
        self.sequence: list = []
        self.target_window_var = ctk.StringVar(value="")
        self.pixel_x_var = ctk.StringVar(value="0")
        self.pixel_y_var = ctk.StringVar(value="0")
        self.pixel_color_var = ctk.StringVar(value="")
        self.region_enabled_var = ctk.BooleanVar(value=False)
        self.region_x_var = ctk.StringVar(value="0")
        self.region_y_var = ctk.StringVar(value="0")
        self.region_w_var = ctk.StringVar(value="0")
        self.region_h_var = ctk.StringVar(value="0")

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_form()
        self._build_sidebar()

    # ---------- public API ----------

    def get_config(self) -> ClickConfig | None:
        try:
            interval = (
                int(self.hours.get() or 0) * 3600
                + int(self.minutes.get() or 0) * 60
                + int(self.seconds.get() or 0)
                + int(self.milliseconds.get() or 0) / 1000.0
            )
            interval = max(0.001, interval)
            return ClickConfig(
                interval_seconds=interval,
                button=self.button_var.get(),  # type: ignore[arg-type]
                click_type=self.click_type_var.get(),  # type: ignore[arg-type]
                repeat_mode=(
                    "fixed_count" if self.repeat_mode_var.get() == "fixed" else "until_stopped"
                ),
                repeat_count=int(self.repeat_count.get() or 1),
                position_mode="fixed" if self.position_mode_var.get() == "fixed" else "current",
                x=int(self.x_var.get() or 0),
                y=int(self.y_var.get() or 0),
                jitter_ms=int(self.jitter_ms_var.get() or 0),
                jitter_pixels=int(self.jitter_px_var.get() or 0),
                sequence=list(self.sequence),
                target_window=self.target_window_var.get().strip(),
                pixel_trigger_x=int(self.pixel_x_var.get() or 0),
                pixel_trigger_y=int(self.pixel_y_var.get() or 0),
                pixel_trigger_color=self.pixel_color_var.get().strip(),
                region_enabled=bool(self.region_enabled_var.get()),
                region_x=int(self.region_x_var.get() or 0),
                region_y=int(self.region_y_var.get() or 0),
                region_width=int(self.region_w_var.get() or 0),
                region_height=int(self.region_h_var.get() or 0),
            )
        except ValueError:
            return None

    def apply_config(self, config: ClickConfig) -> None:
        total_ms = int(round(config.interval_seconds * 1000))
        h, rem = divmod(total_ms, 3_600_000)
        m, rem = divmod(rem, 60_000)
        s, ms = divmod(rem, 1_000)
        self.hours.set(str(h))
        self.minutes.set(str(m))
        self.seconds.set(str(s))
        self.milliseconds.set(str(ms))
        self.button_var.set(config.button)
        self.click_type_var.set(config.click_type)
        self.repeat_mode_var.set("fixed" if config.repeat_mode == "fixed_count" else "loop")
        self.repeat_count.set(str(config.repeat_count))
        self.position_mode_var.set("fixed" if config.position_mode == "fixed" else "current")
        self.x_var.set(str(config.x))
        self.y_var.set(str(config.y))
        self.jitter_ms_var.set(str(config.jitter_ms))
        self.jitter_px_var.set(str(config.jitter_pixels))
        self.sequence = list(config.sequence or [])
        self.target_window_var.set(config.target_window)
        self.pixel_x_var.set(str(config.pixel_trigger_x))
        self.pixel_y_var.set(str(config.pixel_trigger_y))
        self.pixel_color_var.set(config.pixel_trigger_color)
        self.region_enabled_var.set(bool(config.region_enabled))
        self.region_x_var.set(str(config.region_x))
        self.region_y_var.set(str(config.region_y))
        self.region_w_var.set(str(config.region_width))
        self.region_h_var.set(str(config.region_height))
        self._update_sequence_indicator()

    def set_sequence(self, sequence) -> None:
        self.sequence = list(sequence)
        self._update_sequence_indicator()

    def _update_sequence_indicator(self) -> None:
        if not hasattr(self, "sequence_indicator"):
            return
        if self.sequence:
            self.sequence_indicator.configure(
                text=f"⚡ Sequence active — {len(self.sequence)} step(s) override single-click",
                text_color=self.palette["primary"],
            )
        else:
            self.sequence_indicator.configure(
                text="No sequence — single-click mode active.",
                text_color=self.palette["text_muted"],
            )

    def set_running(self, running: bool) -> None:
        if running:
            self.status_pill.set_state("running")
            self.start_button.configure(text="■  Stop", fg_color=self.palette["danger"])
        else:
            self.status_pill.set_state("idle")
            self.start_button.configure(
                text="▶  Start", fg_color=self.palette["primary"]
            )

    def update_count(self, count: int) -> None:
        self.click_tile.set_value(f"{count:,}")
        now = time.monotonic()
        self._cps_window.append(now)
        cutoff = now - 5.0
        self._cps_window = [t_ for t_ in self._cps_window if t_ >= cutoff]
        if len(self._cps_window) >= 2:
            span = self._cps_window[-1] - self._cps_window[0]
            cps = (len(self._cps_window) - 1) / span if span > 0 else 0.0
        else:
            cps = 0.0
        self.cps_tile.set_value(f"{cps:.1f}")

    def update_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette

    # ---------- layout ----------

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(24, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Auto Clicker",
            font=t.FONT_HEADING,
            text_color=self.palette["text"],
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="Configure intervals, randomization, and where to click.",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
        ).grid(row=1, column=0, sticky="w")

        self.status_pill = StatusPill(header, self.palette)
        self.status_pill.grid(row=0, column=1, rowspan=2, sticky="e", padx=(0, 0))

    def _build_form(self) -> None:
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=(24, 12), pady=(8, 24))
        container.grid_columnconfigure(0, weight=1)

        # Interval card
        interval_card = Card(container, self.palette)
        interval_card.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        interval_card.grid_columnconfigure(0, weight=1)
        SectionHeader(
            interval_card, self.palette, "Interval", "Time between each click."
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        row = ctk.CTkFrame(interval_card, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        for i in range(4):
            row.grid_columnconfigure(i, weight=1)

        self.hours = ctk.StringVar(value="0")
        self.minutes = ctk.StringVar(value="0")
        self.seconds = ctk.StringVar(value="0")
        self.milliseconds = ctk.StringVar(value="100")
        LabeledEntry(row, self.palette, "Hours", self.hours).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        LabeledEntry(row, self.palette, "Minutes", self.minutes).grid(
            row=0, column=1, sticky="ew", padx=6
        )
        LabeledEntry(row, self.palette, "Seconds", self.seconds).grid(
            row=0, column=2, sticky="ew", padx=6
        )
        LabeledEntry(row, self.palette, "Milliseconds", self.milliseconds).grid(
            row=0, column=3, sticky="ew", padx=(6, 0)
        )

        # CPS quick-tune slider card
        cps_card = Card(container, self.palette)
        cps_card.grid(row=6, column=0, sticky="ew", pady=14)
        cps_card.grid_columnconfigure(0, weight=1)
        SectionHeader(
            cps_card,
            self.palette,
            "Quick rate (CPS)",
            "Drag to set clicks-per-second; updates the interval fields.",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        cps_row = ctk.CTkFrame(cps_card, fg_color="transparent")
        cps_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        cps_row.grid_columnconfigure(0, weight=1)

        self.cps_value_label = ctk.CTkLabel(
            cps_row,
            text="10 CPS  (100 ms)",
            font=("Segoe UI Variable", 14, "bold"),
            text_color=self.palette["text"],
        )
        self.cps_value_label.grid(row=0, column=0, sticky="w")

        self.cps_slider = ctk.CTkSlider(
            cps_row,
            from_=1,
            to=50,
            number_of_steps=49,
            command=self._on_cps_slider,
            button_color=self.palette["primary"],
            button_hover_color=self.palette["primary_hover"],
            progress_color=self.palette["primary"],
        )
        self.cps_slider.set(10)
        self.cps_slider.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        # Click options card
        options_card = Card(container, self.palette)
        options_card.grid(row=1, column=0, sticky="ew", pady=14)
        options_card.grid_columnconfigure(0, weight=1)
        SectionHeader(
            options_card, self.palette, "Click", "Button, type, and repeat behavior."
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        opt_row = ctk.CTkFrame(options_card, fg_color="transparent")
        opt_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        opt_row.grid_columnconfigure((0, 1), weight=1)

        self.button_var = ctk.StringVar(value="left")
        self.click_type_var = ctk.StringVar(value="single")

        ctk.CTkLabel(
            opt_row,
            text="MOUSE BUTTON",
            font=("Segoe UI", 10, "bold"),
            text_color=self.palette["text_muted"],
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            opt_row,
            text="CLICK TYPE",
            font=("Segoe UI", 10, "bold"),
            text_color=self.palette["text_muted"],
        ).grid(row=0, column=1, sticky="w", padx=(12, 0))

        ctk.CTkSegmentedButton(
            opt_row,
            values=["left", "right", "middle"],
            variable=self.button_var,
            selected_color=self.palette["primary"],
            selected_hover_color=self.palette["primary_hover"],
        ).grid(row=1, column=0, sticky="ew", pady=(2, 0))
        ctk.CTkSegmentedButton(
            opt_row,
            values=["single", "double"],
            variable=self.click_type_var,
            selected_color=self.palette["primary"],
            selected_hover_color=self.palette["primary_hover"],
        ).grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(2, 0))

        # Repeat
        repeat_row = ctk.CTkFrame(options_card, fg_color="transparent")
        repeat_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        repeat_row.grid_columnconfigure(0, weight=1)
        repeat_row.grid_columnconfigure(1, weight=0)

        self.repeat_mode_var = ctk.StringVar(value="loop")
        ctk.CTkLabel(
            repeat_row,
            text="REPEAT",
            font=("Segoe UI", 10, "bold"),
            text_color=self.palette["text_muted"],
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkSegmentedButton(
            repeat_row,
            values=["loop", "fixed"],
            variable=self.repeat_mode_var,
            selected_color=self.palette["primary"],
            selected_hover_color=self.palette["primary_hover"],
        ).grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.repeat_count = ctk.StringVar(value="100")
        LabeledEntry(repeat_row, self.palette, "COUNT", self.repeat_count, width=80).grid(
            row=0, column=1, rowspan=2, padx=(12, 0), sticky="e"
        )

        # Position card
        position_card = Card(container, self.palette)
        position_card.grid(row=2, column=0, sticky="ew", pady=14)
        position_card.grid_columnconfigure(0, weight=1)
        SectionHeader(
            position_card, self.palette, "Position", "Click at the cursor or a fixed point."
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        pos_row = ctk.CTkFrame(position_card, fg_color="transparent")
        pos_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        pos_row.grid_columnconfigure(0, weight=1)
        self.position_mode_var = ctk.StringVar(value="current")
        ctk.CTkSegmentedButton(
            pos_row,
            values=["current", "fixed"],
            variable=self.position_mode_var,
            selected_color=self.palette["primary"],
            selected_hover_color=self.palette["primary_hover"],
        ).grid(row=0, column=0, sticky="ew")

        coord_row = ctk.CTkFrame(position_card, fg_color="transparent")
        coord_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        for i in range(3):
            coord_row.grid_columnconfigure(i, weight=1)
        self.x_var = ctk.StringVar(value="0")
        self.y_var = ctk.StringVar(value="0")
        LabeledEntry(coord_row, self.palette, "X", self.x_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        LabeledEntry(coord_row, self.palette, "Y", self.y_var).grid(
            row=0, column=1, sticky="ew", padx=6
        )
        ctk.CTkButton(
            coord_row,
            text="🎯  Pick (3s)",
            command=self._pick_position,
            fg_color=self.palette["surface_alt"],
            hover_color=self.palette["border"],
            text_color=self.palette["text"],
            corner_radius=10,
        ).grid(row=0, column=2, sticky="sew", padx=(6, 0), pady=(14, 0))

        # Region (random point inside box) — overrides single-point if enabled
        region_check_row = ctk.CTkFrame(position_card, fg_color="transparent")
        region_check_row.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 4))
        ctk.CTkCheckBox(
            region_check_row,
            text="Click random point inside region (overrides above)",
            variable=self.region_enabled_var,
            fg_color=self.palette["primary"],
            hover_color=self.palette["primary_hover"],
            text_color=self.palette["text"],
        ).grid(row=0, column=0, sticky="w")

        region_row = ctk.CTkFrame(position_card, fg_color="transparent")
        region_row.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 18))
        for i in range(5):
            region_row.grid_columnconfigure(i, weight=1)
        LabeledEntry(region_row, self.palette, "REGION X", self.region_x_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        LabeledEntry(region_row, self.palette, "REGION Y", self.region_y_var).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        LabeledEntry(region_row, self.palette, "WIDTH", self.region_w_var).grid(
            row=0, column=2, sticky="ew", padx=4
        )
        LabeledEntry(region_row, self.palette, "HEIGHT", self.region_h_var).grid(
            row=0, column=3, sticky="ew", padx=4
        )
        ctk.CTkButton(
            region_row,
            text="🎯  Top-left",
            command=self._pick_region_origin,
            fg_color=self.palette["surface_alt"],
            hover_color=self.palette["border"],
            text_color=self.palette["text"],
            corner_radius=10,
        ).grid(row=0, column=4, sticky="sew", padx=(4, 0), pady=(14, 0))

        # Targeting card (window + pixel trigger)
        target_card = Card(container, self.palette)
        target_card.grid(row=4, column=0, sticky="ew", pady=14)
        target_card.grid_columnconfigure(0, weight=1)
        SectionHeader(
            target_card,
            self.palette,
            "Targeting",
            "Optional: only click when a window is focused or a pixel matches.",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        win_row = ctk.CTkFrame(target_card, fg_color="transparent")
        win_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
        win_row.grid_columnconfigure(0, weight=1)
        LabeledEntry(
            win_row,
            self.palette,
            "TARGET WINDOW (substring match, blank = any)",
            self.target_window_var,
        ).grid(row=0, column=0, sticky="ew")

        pixel_row = ctk.CTkFrame(target_card, fg_color="transparent")
        pixel_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        for i in range(4):
            pixel_row.grid_columnconfigure(i, weight=1)
        LabeledEntry(pixel_row, self.palette, "PIXEL X", self.pixel_x_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        LabeledEntry(pixel_row, self.palette, "PIXEL Y", self.pixel_y_var).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        LabeledEntry(
            pixel_row, self.palette, "COLOR (#RRGGBB)", self.pixel_color_var
        ).grid(row=0, column=2, sticky="ew", padx=4)
        ctk.CTkButton(
            pixel_row,
            text="🎯  Sample (3s)",
            command=self._sample_pixel,
            fg_color=self.palette["surface_alt"],
            hover_color=self.palette["border"],
            text_color=self.palette["text"],
            corner_radius=10,
        ).grid(row=0, column=3, sticky="sew", padx=(4, 0), pady=(14, 0))

        # Sequence indicator card
        seq_card = Card(container, self.palette)
        seq_card.grid(row=5, column=0, sticky="ew", pady=14)
        seq_card.grid_columnconfigure(0, weight=1)
        SectionHeader(
            seq_card, self.palette, "Sequence", "Multi-target queue (edit on Sequence tab)."
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 6))
        self.sequence_indicator = ctk.CTkLabel(
            seq_card,
            text="No sequence — single-click mode active.",
            font=t.FONT_BODY,
            text_color=self.palette["text_muted"],
            anchor="w",
        )
        self.sequence_indicator.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))

        # Randomization card
        rand_card = Card(container, self.palette)
        rand_card.grid(row=3, column=0, sticky="ew", pady=14)
        rand_card.grid_columnconfigure(0, weight=1)
        SectionHeader(
            rand_card,
            self.palette,
            "Randomization",
            "Add jitter to look more natural.",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        rand_row = ctk.CTkFrame(rand_card, fg_color="transparent")
        rand_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        rand_row.grid_columnconfigure((0, 1), weight=1)
        self.jitter_ms_var = ctk.StringVar(value="0")
        self.jitter_px_var = ctk.StringVar(value="0")
        LabeledEntry(rand_row, self.palette, "TIMING JITTER (MS)", self.jitter_ms_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        LabeledEntry(rand_row, self.palette, "POSITION JITTER (PX)", self.jitter_px_var).grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, fg_color="transparent")
        sidebar.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(12, 24), pady=(8, 24))
        sidebar.grid_columnconfigure(0, weight=1)

        self.start_button = ctk.CTkButton(
            sidebar,
            text="▶  Start",
            command=self._toggle,
            height=64,
            font=("Segoe UI Variable", 18, "bold"),
            fg_color=self.palette["primary"],
            hover_color=self.palette["primary_hover"],
            text_color="#ffffff",
            corner_radius=14,
        )
        self.start_button.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            sidebar,
            text="Hotkey: F6 to start/stop · ESC for emergency stop",
            font=t.FONT_MUTED,
            text_color=self.palette["text_muted"],
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(8, 16))

        self.click_tile = StatTile(sidebar, self.palette, "Clicks this run")
        self.click_tile.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.cps_tile = StatTile(sidebar, self.palette, "Clicks/sec (5s avg)")
        self.cps_tile.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            sidebar,
            text="💾  Save as profile",
            command=self._save_profile,
            fg_color="transparent",
            border_color=self.palette["border"],
            border_width=1,
            text_color=self.palette["text"],
            hover_color=self.palette["surface_alt"],
            height=40,
            corner_radius=10,
        ).grid(row=4, column=0, sticky="ew", pady=(8, 0))

    # ---------- handlers ----------

    def _toggle(self) -> None:
        self.on_start_stop(self.get_config())

    def _save_profile(self) -> None:
        cfg = self.get_config()
        if cfg is not None:
            self.on_save_profile(cfg)

    def _pick_position(self) -> None:
        def receive(x: int, y: int) -> None:
            self.x_var.set(str(x))
            self.y_var.set(str(y))
            self.position_mode_var.set("fixed")

        self.on_pick_position(receive)

    def _on_cps_slider(self, value: float) -> None:
        cps = max(1, int(round(value)))
        ms = max(1, int(round(1000.0 / cps)))
        self.hours.set("0")
        self.minutes.set("0")
        self.seconds.set("0")
        self.milliseconds.set(str(ms))
        self.cps_value_label.configure(text=f"{cps} CPS  ({ms} ms)")

    def _pick_region_origin(self) -> None:
        def receive(x: int, y: int) -> None:
            self.region_x_var.set(str(x))
            self.region_y_var.set(str(y))
            self.region_enabled_var.set(True)

        self.on_pick_position(receive)

    def _sample_pixel(self) -> None:
        def receive(x: int, y: int) -> None:
            self.pixel_x_var.set(str(x))
            self.pixel_y_var.set(str(y))
            try:
                import pyautogui  # type: ignore

                shot = pyautogui.screenshot(region=(int(x), int(y), 1, 1))
                r, g, b = shot.getpixel((0, 0))[:3]
                self.pixel_color_var.set(f"#{r:02X}{g:02X}{b:02X}")
            except Exception:
                pass

        self.on_pick_position(receive)
