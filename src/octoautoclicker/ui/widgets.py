"""Reusable composite widgets: cards, status pills, toasts, sidebar buttons."""

from __future__ import annotations

import customtkinter as ctk

from . import theme as t


class Card(ctk.CTkFrame):
    """Padded surface used as the base for grouped controls."""

    def __init__(self, master, palette: dict[str, str], **kwargs):
        super().__init__(
            master,
            fg_color=palette["surface"],
            border_color=palette["border"],
            border_width=1,
            corner_radius=14,
            **kwargs,
        )


class SectionHeader(ctk.CTkFrame):
    def __init__(self, master, palette: dict[str, str], title: str, subtitle: str = ""):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text=title,
            font=t.FONT_SUBHEADING,
            text_color=palette["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        if subtitle:
            ctk.CTkLabel(
                self,
                text=subtitle,
                font=t.FONT_MUTED,
                text_color=palette["text_muted"],
                anchor="w",
            ).grid(row=1, column=0, sticky="w")


class StatusPill(ctk.CTkFrame):
    """Colored pill that switches between idle/running/recording states."""

    STATES = {
        "idle": ("Idle", "text_muted", "border"),
        "running": ("Clicking", "success", "success"),
        "recording": ("Recording", "danger", "danger"),
        "playing": ("Playing", "primary", "primary"),
        "error": ("Error", "danger", "danger"),
    }

    def __init__(self, master, palette: dict[str, str]):
        super().__init__(master, fg_color="transparent")
        self.palette = palette
        self.dot = ctk.CTkLabel(
            self,
            text="●",
            font=("Segoe UI", 14),
            text_color=palette["text_muted"],
            width=18,
        )
        self.dot.grid(row=0, column=0, padx=(0, 6))
        self.label = ctk.CTkLabel(
            self,
            text="Idle",
            font=t.FONT_SUBHEADING,
            text_color=palette["text"],
        )
        self.label.grid(row=0, column=1)
        self._state = "idle"
        self._pulse_after = None
        self._pulse_phase = 0

    def set_state(self, state: str, label: str | None = None) -> None:
        self._state = state
        text, color_key, _ = self.STATES.get(state, self.STATES["idle"])
        self.label.configure(text=label or text, text_color=self.palette[color_key])
        self.dot.configure(text_color=self.palette[color_key])
        if state in ("running", "recording", "playing"):
            self._start_pulse()
        else:
            self._stop_pulse()

    def _start_pulse(self) -> None:
        if self._pulse_after is not None:
            return
        self._pulse()

    def _pulse(self) -> None:
        self._pulse_phase = (self._pulse_phase + 1) % 2
        size = 16 if self._pulse_phase == 0 else 12
        try:
            self.dot.configure(font=("Segoe UI", size))
            self._pulse_after = self.after(420, self._pulse)
        except Exception:
            self._pulse_after = None

    def _stop_pulse(self) -> None:
        if self._pulse_after is not None:
            try:
                self.after_cancel(self._pulse_after)
            except Exception:
                pass
            self._pulse_after = None
        try:
            self.dot.configure(font=("Segoe UI", 14))
        except Exception:
            pass


class StatTile(ctk.CTkFrame):
    """Small card showing a label + big number."""

    def __init__(self, master, palette: dict[str, str], label: str, value: str = "0"):
        super().__init__(
            master,
            fg_color=palette["surface_alt"],
            corner_radius=12,
            border_color=palette["border"],
            border_width=1,
        )
        ctk.CTkLabel(
            self,
            text=label.upper(),
            font=("Segoe UI", 10, "bold"),
            text_color=palette["text_muted"],
        ).pack(anchor="w", padx=14, pady=(10, 0))
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=t.FONT_LARGE_NUMBER,
            text_color=palette["text"],
        )
        self.value_label.pack(anchor="w", padx=14, pady=(0, 10))

    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)


class SidebarButton(ctk.CTkButton):
    """Nav button in the left sidebar with active/inactive states."""

    def __init__(self, master, palette: dict[str, str], text: str, icon: str, command):
        self.palette = palette
        super().__init__(
            master,
            text=f"  {icon}   {text}",
            anchor="w",
            command=command,
            corner_radius=10,
            height=42,
            font=("Segoe UI", 13),
            fg_color="transparent",
            hover_color=palette["surface_alt"],
            text_color=palette["text_muted"],
        )
        self._active = False

    def set_active(self, active: bool) -> None:
        self._active = active
        if active:
            self.configure(
                fg_color=self.palette["surface_alt"],
                text_color=self.palette["primary"],
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=self.palette["text_muted"],
            )


class Toast(ctk.CTkFrame):
    """Transient notification anchored to the bottom-right of a parent."""

    def __init__(self, master, palette: dict[str, str], message: str, kind: str = "info"):
        color_key = {
            "info": "primary",
            "success": "success",
            "warning": "warning",
            "error": "danger",
        }.get(kind, "primary")
        super().__init__(
            master,
            fg_color=palette["surface"],
            border_color=palette[color_key],
            border_width=1,
            corner_radius=10,
        )
        accent_bar = ctk.CTkFrame(
            self, fg_color=palette[color_key], width=4, corner_radius=2
        )
        accent_bar.pack(side="left", fill="y", padx=(8, 8), pady=8)
        ctk.CTkLabel(
            self, text=message, font=t.FONT_BODY, text_color=palette["text"], wraplength=320
        ).pack(side="left", padx=(0, 14), pady=10)


class ToastStack:
    """Stacks toasts in the bottom-right of a window and auto-dismisses them."""

    def __init__(self, master, palette: dict[str, str]):
        self.master = master
        self.palette = palette
        self._toasts: list[Toast] = []

    def update_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette

    def show(self, message: str, kind: str = "info", duration_ms: int = 3200) -> None:
        toast = Toast(self.master, self.palette, message, kind)
        self._toasts.append(toast)
        self._reposition()
        self.master.after(duration_ms, lambda: self._dismiss(toast))

    def _dismiss(self, toast: Toast) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
        try:
            toast.place_forget()
            toast.destroy()
        except Exception:
            pass
        self._reposition()

    def _reposition(self) -> None:
        try:
            self.master.update_idletasks()
            base_y = self.master.winfo_height() - 24
            for toast in reversed(self._toasts):
                toast.update_idletasks()
                h = toast.winfo_reqheight()
                w = toast.winfo_reqwidth()
                base_y -= h + 8
                toast.place(
                    x=self.master.winfo_width() - w - 24,
                    y=base_y,
                )
        except Exception:
            pass


class LabeledEntry(ctk.CTkFrame):
    """Compact label-on-top entry."""

    def __init__(
        self,
        master,
        palette: dict[str, str],
        label: str,
        textvariable,
        width: int = 90,
    ):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(
            self,
            text=label,
            font=("Segoe UI", 10, "bold"),
            text_color=palette["text_muted"],
        ).pack(anchor="w")
        ctk.CTkEntry(
            self,
            textvariable=textvariable,
            width=width,
            fg_color=palette["surface_alt"],
            border_color=palette["border"],
            text_color=palette["text"],
        ).pack(fill="x")
