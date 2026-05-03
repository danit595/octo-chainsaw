"""Persistent settings, profiles, and stats."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .models import ClickConfig, HotkeyConfig, Profile, Stats


def default_data_dir() -> Path:
    """Per-user data directory. %APPDATA% on Windows, ~/.config elsewhere."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "OctoAutoClicker"


@dataclass
class AppSettings:
    """Top-level user settings persisted to disk."""

    theme: str = "dark"
    accent: str = "violet"
    minimize_on_start: bool = False
    show_toasts: bool = True
    last_profile: str = "Default"
    hotkeys: HotkeyConfig = field(default_factory=HotkeyConfig)

    def to_dict(self) -> dict:
        return {
            "theme": self.theme,
            "accent": self.accent,
            "minimize_on_start": self.minimize_on_start,
            "show_toasts": self.show_toasts,
            "last_profile": self.last_profile,
            "hotkeys": self.hotkeys.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        return cls(
            theme=data.get("theme", "dark"),
            accent=data.get("accent", "violet"),
            minimize_on_start=data.get("minimize_on_start", False),
            show_toasts=data.get("show_toasts", True),
            last_profile=data.get("last_profile", "Default"),
            hotkeys=HotkeyConfig.from_dict(data.get("hotkeys", {})),
        )


class ConfigStore:
    """Loads/saves settings, profiles, and stats from a per-user directory."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or default_data_dir()
        self.settings_file = self.data_dir / "settings.json"
        self.profiles_file = self.data_dir / "profiles.json"
        self.stats_file = self.data_dir / "stats.json"
        self.macros_dir = self.data_dir / "macros"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.macros_dir.mkdir(parents=True, exist_ok=True)

    def load_settings(self) -> AppSettings:
        if not self.settings_file.exists():
            return AppSettings()
        try:
            return AppSettings.from_dict(json.loads(self.settings_file.read_text("utf-8")))
        except (json.JSONDecodeError, OSError):
            return AppSettings()

    def save_settings(self, settings: AppSettings) -> None:
        self.settings_file.write_text(
            json.dumps(settings.to_dict(), indent=2), encoding="utf-8"
        )

    def load_profiles(self) -> list[Profile]:
        if not self.profiles_file.exists():
            return [Profile(name="Default", config=ClickConfig())]
        try:
            data = json.loads(self.profiles_file.read_text("utf-8"))
            profiles = [Profile.from_dict(p) for p in data]
            return profiles or [Profile(name="Default", config=ClickConfig())]
        except (json.JSONDecodeError, OSError, KeyError):
            return [Profile(name="Default", config=ClickConfig())]

    def save_profiles(self, profiles: list[Profile]) -> None:
        self.profiles_file.write_text(
            json.dumps([p.to_dict() for p in profiles], indent=2), encoding="utf-8"
        )

    def load_stats(self) -> Stats:
        if not self.stats_file.exists():
            return Stats()
        try:
            return Stats.from_dict(json.loads(self.stats_file.read_text("utf-8")))
        except (json.JSONDecodeError, OSError):
            return Stats()

    def save_stats(self, stats: Stats) -> None:
        self.stats_file.write_text(
            json.dumps(stats.to_dict(), indent=2), encoding="utf-8"
        )
