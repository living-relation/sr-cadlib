"""Tests for the JSON part registry. No Fusion required except reg_file()."""
from __future__ import annotations

from pathlib import Path

import pytest

from sr_cadlib import configure, reg_file, reg_load, reg_put
from tests import adsk_stub


def _setup(tmp_path: Path) -> Path:
    registry = tmp_path / "registry.json"
    configure(
        project="MyProject",
        root="Products/Widget",
        registry_path=registry,
        log_path=tmp_path / "build.log",
    )
    return registry


def test_reg_load_missing_is_empty(tmp_path: Path):
    _setup(tmp_path)
    assert reg_load() == {}
    assert not (tmp_path / "registry.json").exists()


def test_reg_put_and_load(tmp_path: Path):
    registry = _setup(tmp_path)
    reg_put("block", {"id": "urn:example:1", "name": "Block", "pn": "BLK-1", "desc": "A block", "folder": "Products/Widget/Custom Parts"})
    data = reg_load()
    assert data["block"]["id"] == "urn:example:1"
    assert data["block"]["pn"] == "BLK-1"
    raw = registry.read_text(encoding="utf-8")
    assert '"block"' in raw
    # indent=1, same as the original helper
    assert "\n " in raw


def test_reg_put_replaces_key(tmp_path: Path):
    _setup(tmp_path)
    reg_put("block", {"id": "one"})
    reg_put("block", {"id": "two"})
    reg_put("pin", {"id": "three"})
    data = reg_load()
    assert data["block"]["id"] == "two"
    assert data["pin"]["id"] == "three"


def test_reg_file_missing_key(tmp_path: Path):
    _setup(tmp_path)
    with pytest.raises(Exception, match="registry missing"):
        reg_file("nope")


def test_reg_file_missing_fusion_file(tmp_path: Path):
    _setup(tmp_path)
    reg_put("block", {"id": "urn:missing"})
    with pytest.raises(Exception, match="file not found"):
        reg_file("block")


def test_reg_file_finds_id(tmp_path: Path):
    _setup(tmp_path)
    adsk_stub._APP.data._files["urn:found"] = adsk_stub._Named("Block")
    adsk_stub._APP.data._files["urn:found"].id = "urn:found"
    reg_put("block", {"id": "urn:found"})
    df = reg_file("block")
    assert df.id == "urn:found"
    assert df.name == "Block"
