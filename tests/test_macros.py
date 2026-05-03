from pathlib import Path

from octoautoclicker.engines.macros import (
    delete_macro,
    list_macros,
    load_macro,
    save_macro,
)
from octoautoclicker.models import Macro, MacroEvent


def _sample_macro(name: str = "demo") -> Macro:
    return Macro(
        name=name,
        events=[
            MacroEvent(type="move", time=0.0, x=0, y=0),
            MacroEvent(type="click", time=0.5, button="left", x=10, y=10),
            MacroEvent(type="key", time=1.0, key="a", pressed=True),
            MacroEvent(type="key", time=1.05, key="a", pressed=False),
        ],
    )


def test_save_and_load_macro_round_trip(tmp_path: Path):
    macro = _sample_macro("round-trip")
    path = save_macro(macro, tmp_path)
    assert path.exists()
    loaded = load_macro(path)
    assert loaded.name == "round-trip"
    assert len(loaded.events) == len(macro.events)
    assert loaded.events[1].button == "left"
    assert loaded.events[2].key == "a"
    assert loaded.events[2].pressed is True


def test_list_macros_returns_sorted_names(tmp_path: Path):
    save_macro(_sample_macro("zeta"), tmp_path)
    save_macro(_sample_macro("alpha"), tmp_path)
    save_macro(_sample_macro("mike"), tmp_path)
    assert list_macros(tmp_path) == ["alpha", "mike", "zeta"]


def test_list_macros_empty_dir(tmp_path: Path):
    assert list_macros(tmp_path / "missing") == []


def test_delete_macro_removes_file(tmp_path: Path):
    save_macro(_sample_macro("doomed"), tmp_path)
    assert "doomed" in list_macros(tmp_path)
    assert delete_macro("doomed", tmp_path) is True
    assert "doomed" not in list_macros(tmp_path)


def test_delete_missing_macro_returns_false(tmp_path: Path):
    assert delete_macro("ghost", tmp_path) is False


def test_load_macro_supplies_name_from_filename(tmp_path: Path):
    path = tmp_path / "no-name.json"
    path.write_text('{"events": []}', encoding="utf-8")
    macro = load_macro(path)
    assert macro.name == "no-name"
