from pathlib import Path

from octoautoclicker.config import AppSettings, ConfigStore
from octoautoclicker.models import ClickConfig, HotkeyConfig, Profile, Stats


def test_store_creates_directories(tmp_path: Path):
    store = ConfigStore(tmp_path / "data")
    assert store.data_dir.exists()
    assert store.macros_dir.exists()


def test_settings_default_when_missing(tmp_path: Path):
    store = ConfigStore(tmp_path)
    settings = store.load_settings()
    assert settings.theme == "dark"
    assert settings.accent == "violet"
    assert settings.hotkeys == HotkeyConfig()


def test_settings_round_trip(tmp_path: Path):
    store = ConfigStore(tmp_path)
    settings = AppSettings(
        theme="light",
        accent="emerald",
        minimize_on_start=True,
        show_toasts=False,
        last_profile="Speed",
        hotkeys=HotkeyConfig(toggle_clicker="ctrl+1"),
        start_delay_seconds=5,
        failsafe_enabled=False,
        sound_enabled=True,
    )
    store.save_settings(settings)
    restored = store.load_settings()
    assert restored == settings
    assert restored.start_delay_seconds == 5
    assert restored.failsafe_enabled is False
    assert restored.sound_enabled is True


def test_profiles_default_seed(tmp_path: Path):
    store = ConfigStore(tmp_path)
    profiles = store.load_profiles()
    assert len(profiles) == 1
    assert profiles[0].name == "Default"


def test_profiles_round_trip(tmp_path: Path):
    store = ConfigStore(tmp_path)
    profiles = [
        Profile(name="Fast", config=ClickConfig(interval_seconds=0.005)),
        Profile(name="Burst", config=ClickConfig(repeat_mode="fixed_count", repeat_count=10)),
    ]
    store.save_profiles(profiles)
    restored = store.load_profiles()
    assert [p.name for p in restored] == ["Fast", "Burst"]
    assert restored[0].config.interval_seconds == 0.005
    assert restored[1].config.repeat_count == 10


def test_stats_round_trip(tmp_path: Path):
    store = ConfigStore(tmp_path)
    stats = Stats(total_clicks=99, total_sessions=4, total_seconds_active=12.5, macros_played=3)
    store.save_stats(stats)
    assert store.load_stats() == stats


def test_settings_corrupt_file_falls_back(tmp_path: Path):
    store = ConfigStore(tmp_path)
    store.settings_file.write_text("{not json", encoding="utf-8")
    settings = store.load_settings()
    assert settings == AppSettings()
