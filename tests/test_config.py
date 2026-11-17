"""Tests for configure(), path helpers and unit constants. No Fusion required."""
from __future__ import annotations

from pathlib import Path

import pytest

from sr_cadlib import (
    ConfigError,
    F_ASSY,
    F_FAB,
    F_PURCH,
    IN,
    LIBDIR,
    MM,
    PROJECT,
    REGF,
    ROOT,
    configure,
    current_config,
    folder_paths,
    is_configured,
    log,
    project_name,
    reset_config,
)


def test_units():
    assert MM == 0.1
    assert IN == 2.54
    assert 10 * MM == 1.0
    assert 1 * IN == 2.54


def test_folder_paths_defaults():
    paths = folder_paths("Products/Widget")
    assert paths["purchased_path"] == "Products/Widget/Purchased Parts"
    assert paths["fabricated_path"] == "Products/Widget/Fabricated Parts"
    assert paths["assembly_path"] == "Products/Widget/Subassemblies"


def test_folder_paths_custom_names():
    paths = folder_paths(
        "Team/Line",
        purchased_folder="Off the Shelf",
        fabricated_folder="Custom Parts",
        assembly_folder="Assemblies",
    )
    assert paths["purchased_path"] == "Team/Line/Off the Shelf"
    assert paths["fabricated_path"] == "Team/Line/Custom Parts"
    assert paths["assembly_path"] == "Team/Line/Assemblies"


def test_folder_paths_strips_slashes():
    paths = folder_paths("/Products/Widget/")
    assert paths["purchased_path"] == "Products/Widget/Purchased Parts"


def test_not_configured():
    assert is_configured() is False
    with pytest.raises(ConfigError, match="configure"):
        current_config()
    with pytest.raises(ConfigError):
        str(PROJECT)
    with pytest.raises(ConfigError):
        project_name()


def test_configure_requires_project_and_root(tmp_path: Path):
    with pytest.raises(ConfigError, match="project"):
        configure(
            project="  ",
            root="Products/Widget",
            registry_path=tmp_path / "registry.json",
            log_path=tmp_path / "build.log",
        )
    with pytest.raises(ConfigError, match="root"):
        configure(
            project="MyProject",
            root="",
            registry_path=tmp_path / "registry.json",
            log_path=tmp_path / "build.log",
        )


def test_configure_sets_live_paths(tmp_path: Path):
    configure(
        project="MyProject",
        root="Products/Widget",
        registry_path=tmp_path / "registry.json",
        log_path=tmp_path / "logs" / "build.log",
    )
    assert is_configured() is True
    assert PROJECT == "MyProject"
    assert ROOT == "Products/Widget"
    assert project_name() == "MyProject"
    assert F_PURCH == "Products/Widget/Purchased Parts"
    assert F_FAB == "Products/Widget/Fabricated Parts"
    assert F_ASSY == "Products/Widget/Subassemblies"
    assert REGF == str(tmp_path / "registry.json")
    assert LIBDIR == str(tmp_path)
    cfg = current_config()
    assert cfg["project"] == "MyProject"
    assert cfg["purchased_path"] == "Products/Widget/Purchased Parts"
    assert cfg["log_path"] == str(tmp_path / "logs" / "build.log")


def test_live_strings_follow_reconfigure(tmp_path: Path):
    # Imported names stay correct after a later configure() call.
    configure(
        project="Alpha",
        root="Line/A",
        registry_path=tmp_path / "a.json",
        log_path=tmp_path / "a.log",
    )
    assert PROJECT == "Alpha"
    assert F_PURCH == "Line/A/Purchased Parts"
    configure(
        project="Beta",
        root="Line/B",
        registry_path=tmp_path / "b.json",
        log_path=tmp_path / "b.log",
        purchased_folder="Hardware",
        work_dir=tmp_path / "work",
    )
    assert PROJECT == "Beta"
    assert F_PURCH == "Line/B/Hardware"
    assert LIBDIR == str(tmp_path / "work")
    assert (tmp_path / "work").is_dir()


def test_live_string_concat(tmp_path: Path):
    configure(
        project="MyProject",
        root="Products/Widget",
        registry_path=tmp_path / "registry.json",
        log_path=tmp_path / "build.log",
    )
    assert F_PURCH + "/Bracket" == "Products/Widget/Purchased Parts/Bracket"
    assert "prefix:" + PROJECT == "prefix:MyProject"


def test_log_appends(tmp_path: Path, capsys):
    log_path = tmp_path / "build.log"
    configure(
        project="MyProject",
        root="Products/Widget",
        registry_path=tmp_path / "registry.json",
        log_path=log_path,
    )
    log("hello")
    log("again")
    text = log_path.read_text(encoding="utf-8")
    assert "hello\n" in text
    assert "again\n" in text
    out = capsys.readouterr().out
    assert "hello" in out
    assert "again" in out


def test_reset_config(tmp_path: Path):
    configure(
        project="MyProject",
        root="Products/Widget",
        registry_path=tmp_path / "registry.json",
        log_path=tmp_path / "build.log",
    )
    reset_config()
    assert is_configured() is False
