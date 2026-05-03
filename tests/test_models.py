from octoautoclicker.models import (
    ClickConfig,
    HotkeyConfig,
    Macro,
    MacroEvent,
    Profile,
    Stats,
)


def test_click_config_round_trip():
    cfg = ClickConfig(
        interval_seconds=0.25,
        button="right",
        click_type="double",
        repeat_mode="fixed_count",
        repeat_count=42,
        position_mode="fixed",
        x=100,
        y=200,
        jitter_ms=15,
        jitter_pixels=3,
    )
    restored = ClickConfig.from_dict(cfg.to_dict())
    assert restored == cfg


def test_click_config_ignores_unknown_keys():
    data = ClickConfig().to_dict()
    data["unknown"] = "ignored"
    restored = ClickConfig.from_dict(data)
    assert restored == ClickConfig()


def test_profile_round_trip():
    profile = Profile(name="Speed", config=ClickConfig(interval_seconds=0.01))
    restored = Profile.from_dict(profile.to_dict())
    assert restored.name == "Speed"
    assert restored.config.interval_seconds == 0.01


def test_macro_event_round_trip_omits_none():
    event = MacroEvent(type="click", time=1.5, button="left", x=10, y=20)
    data = event.to_dict()
    assert "key" not in data and "pressed" not in data
    restored = MacroEvent.from_dict(data)
    assert restored == event


def test_macro_duration_is_last_event_time():
    macro = Macro(
        name="m",
        events=[
            MacroEvent(type="move", time=0.0, x=0, y=0),
            MacroEvent(type="click", time=2.5, button="left"),
        ],
    )
    assert macro.duration == 2.5


def test_macro_duration_empty():
    assert Macro(name="empty").duration == 0.0


def test_hotkey_config_defaults():
    hk = HotkeyConfig()
    assert hk.toggle_clicker == "f6"
    assert hk.toggle_recording == "f7"
    assert hk.toggle_playback == "f8"
    assert hk.emergency_stop == "esc"


def test_stats_round_trip():
    stats = Stats(total_clicks=10, total_sessions=2, total_seconds_active=5.5, macros_played=1)
    assert Stats.from_dict(stats.to_dict()) == stats
