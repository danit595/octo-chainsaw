"""Typed data models shared across the app."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

MouseButton = Literal["left", "right", "middle"]
ClickType = Literal["single", "double"]
RepeatMode = Literal["until_stopped", "fixed_count"]
PositionMode = Literal["current", "fixed"]


@dataclass
class SequenceStep:
    """A single step in a click sequence: where, which button, post-delay."""

    x: int = 0
    y: int = 0
    button: MouseButton = "left"
    click_type: ClickType = "single"
    delay_ms: int = 100

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SequenceStep":
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass
class ClickConfig:
    """Immutable-ish snapshot of clicker settings consumed by the engine."""

    interval_seconds: float = 0.1
    button: MouseButton = "left"
    click_type: ClickType = "single"
    repeat_mode: RepeatMode = "until_stopped"
    repeat_count: int = 100
    position_mode: PositionMode = "current"
    x: int = 0
    y: int = 0
    jitter_ms: int = 0
    jitter_pixels: int = 0
    sequence: list[SequenceStep] = field(default_factory=list)
    target_window: str = ""
    pixel_trigger_x: int = 0
    pixel_trigger_y: int = 0
    pixel_trigger_color: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["sequence"] = [s for s in data["sequence"]]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ClickConfig":
        allowed = {f for f in cls.__dataclass_fields__}
        kwargs = {k: v for k, v in data.items() if k in allowed}
        if "sequence" in kwargs and kwargs["sequence"] is not None:
            kwargs["sequence"] = [
                SequenceStep.from_dict(s) if isinstance(s, dict) else s
                for s in kwargs["sequence"]
            ]
        return cls(**kwargs)


@dataclass
class Profile:
    """A named, saveable clicker configuration."""

    name: str
    config: ClickConfig = field(default_factory=ClickConfig)

    def to_dict(self) -> dict:
        return {"name": self.name, "config": self.config.to_dict()}

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        return cls(
            name=data["name"],
            config=ClickConfig.from_dict(data.get("config", {})),
        )


EventType = Literal["move", "click", "key"]


@dataclass
class MacroEvent:
    """A single recorded input event."""

    type: EventType
    time: float
    x: int | None = None
    y: int | None = None
    button: MouseButton | None = None
    key: str | None = None
    pressed: bool | None = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> "MacroEvent":
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass
class Macro:
    """A named sequence of recorded events."""

    name: str
    events: list[MacroEvent] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.events[-1].time if self.events else 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "events": [e.to_dict() for e in self.events],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Macro":
        return cls(
            name=data.get("name", "unnamed"),
            events=[MacroEvent.from_dict(e) for e in data.get("events", [])],
        )


@dataclass
class HotkeyConfig:
    """User-customizable hotkey bindings."""

    toggle_clicker: str = "f6"
    toggle_recording: str = "f7"
    toggle_playback: str = "f8"
    emergency_stop: str = "esc"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "HotkeyConfig":
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass
class Stats:
    """Lifetime usage stats."""

    total_clicks: int = 0
    total_sessions: int = 0
    total_seconds_active: float = 0.0
    macros_played: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Stats":
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})
