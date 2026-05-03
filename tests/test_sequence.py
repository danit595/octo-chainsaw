"""Sequence model + clicker sequence dispatch with stubbed pyautogui."""

import sys
import threading
import types

import pytest

from octoautoclicker.models import ClickConfig, SequenceStep


def test_sequence_step_round_trip():
    step = SequenceStep(x=10, y=20, button="right", click_type="double", delay_ms=250)
    restored = SequenceStep.from_dict(step.to_dict())
    assert restored == step


def test_click_config_carries_sequence_through_round_trip():
    cfg = ClickConfig(
        sequence=[
            SequenceStep(x=1, y=2, button="left"),
            SequenceStep(x=3, y=4, button="right", click_type="double", delay_ms=500),
        ],
        target_window="Notepad",
        pixel_trigger_x=100,
        pixel_trigger_y=200,
        pixel_trigger_color="#FF8800",
    )
    restored = ClickConfig.from_dict(cfg.to_dict())
    assert restored.target_window == "Notepad"
    assert restored.pixel_trigger_color == "#FF8800"
    assert len(restored.sequence) == 2
    assert restored.sequence[1].click_type == "double"
    assert restored.sequence[1].delay_ms == 500


class _Stub:
    class FailSafeException(Exception):
        pass

    def __init__(self):
        self.click_calls = []
        self.move_calls = []
        self._position = (10, 10)

    def click(self, button="left", _pause=False):
        self.click_calls.append(button)

    def doubleClick(self, button="left", _pause=False):
        self.click_calls.append(f"double:{button}")

    def moveTo(self, x, y, _pause=False):
        self.move_calls.append((x, y))

    def position(self):
        return self._position


@pytest.fixture
def engine_module(monkeypatch):
    fake = types.ModuleType("pyautogui")
    stub = _Stub()
    fake.click = stub.click
    fake.doubleClick = stub.doubleClick
    fake.moveTo = stub.moveTo
    fake.position = stub.position
    fake.FailSafeException = stub.FailSafeException
    monkeypatch.setitem(sys.modules, "pyautogui", fake)
    sys.modules.pop("octoautoclicker.engines.clicker", None)
    from octoautoclicker.engines import clicker as engine_module

    engine_module.pyautogui = fake
    engine_module.pygetwindow = None  # disable window filter
    return engine_module, stub


def test_sequence_dispatch_visits_each_step(engine_module):
    module, stub = engine_module
    done = threading.Event()

    engine = module.ClickerEngine(
        on_state_change=lambda r: None if r else done.set(),
    )
    cfg = ClickConfig(
        repeat_mode="fixed_count",
        repeat_count=3,
        sequence=[
            SequenceStep(x=10, y=10, button="left", delay_ms=1),
            SequenceStep(x=20, y=20, button="right", delay_ms=1),
            SequenceStep(x=30, y=30, button="middle", click_type="double", delay_ms=1),
        ],
    )
    engine.start(cfg)
    assert done.wait(2.0)
    assert (10, 10) in stub.move_calls
    assert (20, 20) in stub.move_calls
    assert (30, 30) in stub.move_calls
    assert "left" in stub.click_calls
    assert "right" in stub.click_calls
    assert "double:middle" in stub.click_calls


def test_color_parser_handles_hex_with_or_without_hash(engine_module):
    module, _ = engine_module
    assert module.ClickerEngine._parse_color("#FF8800") == (255, 136, 0)
    assert module.ClickerEngine._parse_color("00aa55") == (0, 170, 85)
    assert module.ClickerEngine._parse_color("invalid") is None
    assert module.ClickerEngine._parse_color("") is None
