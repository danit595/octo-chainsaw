"""Tests that exercise the clicker engine's loop without the GUI.

We monkey-patch pyautogui to a stub so the engine can run headlessly.
"""

import sys
import threading
import time
import types

import pytest


class _StubPyAutoGUI:
    """Minimal pyautogui stub: counts calls and records arguments."""

    class FailSafeException(Exception):
        pass

    def __init__(self):
        self.click_calls = []
        self.double_click_calls = []
        self.move_calls = []
        self._position = (500, 500)

    def click(self, button="left", _pause=False):
        self.click_calls.append(button)

    def doubleClick(self, button="left", _pause=False):
        self.double_click_calls.append(button)

    def moveTo(self, x, y, _pause=False):
        self.move_calls.append((x, y))

    def position(self):
        return self._position


@pytest.fixture
def clicker_module(monkeypatch):
    """Provide the clicker engine module with a stub pyautogui injected."""
    stub = _StubPyAutoGUI()
    fake_module = types.ModuleType("pyautogui")
    fake_module.click = stub.click
    fake_module.doubleClick = stub.doubleClick
    fake_module.moveTo = stub.moveTo
    fake_module.position = stub.position
    fake_module.FailSafeException = stub.FailSafeException
    monkeypatch.setitem(sys.modules, "pyautogui", fake_module)

    # Import after stubbing so the engine binds to our fake module
    sys.modules.pop("octoautoclicker.engines.clicker", None)
    from octoautoclicker.engines import clicker as engine_module

    engine_module.pyautogui = fake_module
    return engine_module, stub


def test_clicker_runs_fixed_count(clicker_module):
    engine_module, stub = clicker_module
    from octoautoclicker.models import ClickConfig

    done = threading.Event()
    counts: list[int] = []

    def on_state(running: bool) -> None:
        if not running and counts:
            done.set()

    engine = engine_module.ClickerEngine(
        on_click=lambda c: counts.append(c),
        on_state_change=on_state,
    )
    cfg = ClickConfig(
        interval_seconds=0.001,
        repeat_mode="fixed_count",
        repeat_count=5,
    )
    assert engine.start(cfg)
    assert done.wait(2.0)
    assert engine.count == 5
    assert len(stub.click_calls) == 5


def test_double_click_dispatches_double(clicker_module):
    engine_module, stub = clicker_module
    from octoautoclicker.models import ClickConfig

    done = threading.Event()
    engine = engine_module.ClickerEngine(
        on_state_change=lambda r: None if r else done.set(),
    )
    cfg = ClickConfig(
        interval_seconds=0.001,
        click_type="double",
        repeat_mode="fixed_count",
        repeat_count=2,
    )
    engine.start(cfg)
    assert done.wait(2.0)
    assert len(stub.double_click_calls) == 2
    assert stub.click_calls == []


def test_fixed_position_moves_first(clicker_module):
    engine_module, stub = clicker_module
    from octoautoclicker.models import ClickConfig

    done = threading.Event()
    engine = engine_module.ClickerEngine(
        on_state_change=lambda r: None if r else done.set(),
    )
    cfg = ClickConfig(
        interval_seconds=0.001,
        repeat_mode="fixed_count",
        repeat_count=1,
        position_mode="fixed",
        x=42,
        y=99,
    )
    engine.start(cfg)
    assert done.wait(2.0)
    assert (42, 99) in stub.move_calls


def test_region_mode_targets_inside_box(clicker_module):
    engine_module, stub = clicker_module
    from octoautoclicker.models import ClickConfig

    done = threading.Event()
    engine = engine_module.ClickerEngine(
        on_state_change=lambda r: None if r else done.set(),
    )
    cfg = ClickConfig(
        interval_seconds=0.001,
        repeat_mode="fixed_count",
        repeat_count=20,
        region_enabled=True,
        region_x=100,
        region_y=200,
        region_width=50,
        region_height=30,
    )
    engine.start(cfg)
    assert done.wait(2.0)
    assert len(stub.move_calls) == 20
    for x, y in stub.move_calls:
        assert 100 <= x < 150
        assert 200 <= y < 230


def test_stop_halts_loop(clicker_module):
    engine_module, stub = clicker_module
    from octoautoclicker.models import ClickConfig

    engine = engine_module.ClickerEngine()
    cfg = ClickConfig(interval_seconds=0.005)  # loop forever
    engine.start(cfg)
    time.sleep(0.05)
    engine.stop()
    time.sleep(0.05)
    assert not engine.running
    snapshot = engine.count
    time.sleep(0.05)
    assert engine.count == snapshot
