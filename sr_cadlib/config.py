"""Configuration for Fusion project, folder root, registry and log paths.

Call :func:`configure` once at the start of a build script before using folder
paths, the registry, or :func:`log`. There are no built-in project or machine
paths; every workspace value is passed in.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import os
import time

# Fusion's internal length unit is centimetres. Helpers that take millimetres
# or inches multiply by these factors.
MM = 0.1
IN = 2.54

_DEFAULT_PURCHASED = "Purchased Parts"
_DEFAULT_FABRICATED = "Fabricated Parts"
_DEFAULT_ASSEMBLY = "Subassemblies"


class ConfigError(RuntimeError):
    """Raised when the library is used before :func:`configure` is called."""


class _State:
    configured: bool = False
    project: str = ""
    root: str = ""
    registry_path: Path | None = None
    log_path: Path | None = None
    work_dir: Path | None = None
    purchased_folder: str = _DEFAULT_PURCHASED
    fabricated_folder: str = _DEFAULT_FABRICATED
    assembly_folder: str = _DEFAULT_ASSEMBLY


def _require() -> None:
    if not _State.configured:
        raise ConfigError(
            "sr_cadlib.configure() must be called before using project, folder, "
            "registry or log helpers."
        )


def _join_root(root: str, name: str) -> str:
    root = root.strip().strip("/")
    name = name.strip().strip("/")
    if not name:
        return root
    return root + "/" + name


class _LiveStr:
    """A path or name that always reflects the current :func:`configure` values.

    ``from sr_cadlib import F_PURCH`` stays correct after a later
    :func:`configure` call, because this object looks up the value on use.
    """

    def __init__(self, key: str) -> None:
        self._key = key

    def _value(self) -> str:
        _require()
        return str(current_config()[self._key])

    def __str__(self) -> str:
        return self._value()

    def __repr__(self) -> str:
        if not _State.configured:
            return f"<unconfigured {self._key}>"
        return self._value()

    def __fspath__(self) -> str:
        return self._value()

    def __add__(self, other: object) -> str:
        return self._value() + str(other)

    def __radd__(self, other: object) -> str:
        return str(other) + self._value()

    def __eq__(self, other: object) -> bool:
        return self._value() == other

    def __hash__(self) -> int:  # pragma: no cover - strings used as dict keys are rare
        return hash(self._value())

    def __format__(self, spec: str) -> str:
        return format(self._value(), spec)


# Public names kept for compatibility with existing build scripts.
# They are live: read them after configure().
PROJECT = _LiveStr("project")
ROOT = _LiveStr("root")
LIBDIR = _LiveStr("work_dir")
REGF = _LiveStr("registry_path")
F_PURCH = _LiveStr("purchased_path")
F_FAB = _LiveStr("fabricated_path")
F_ASSY = _LiveStr("assembly_path")


def configure(
    *,
    project: str,
    root: str,
    registry_path: str | os.PathLike[str],
    log_path: str | os.PathLike[str],
    purchased_folder: str = _DEFAULT_PURCHASED,
    fabricated_folder: str = _DEFAULT_FABRICATED,
    assembly_folder: str = _DEFAULT_ASSEMBLY,
    work_dir: str | os.PathLike[str] | None = None,
) -> None:
    """Set the Fusion project, folder root, registry file and log file.

    Parameters
    ----------
    project:
        Name of the Fusion data project to open and save into.
    root:
        Folder path inside that project, using ``/`` separators
        (for example ``Products/Widget``).
    registry_path:
        JSON file that maps part keys to saved Fusion file ids.
    log_path:
        Text file that :func:`log` appends to.
    purchased_folder, fabricated_folder, assembly_folder:
        Folder names under ``root`` for purchased parts, fabricated parts and
        subassemblies. The defaults are ``Purchased Parts``,
        ``Fabricated Parts`` and ``Subassemblies``.
    work_dir:
        Optional working directory exposed as :data:`LIBDIR`. When omitted,
        it is the directory that contains the registry file.
    """
    project = (project or "").strip()
    root = (root or "").strip()
    if not project:
        raise ConfigError("project is required")
    if not root:
        raise ConfigError("root is required")
    purchased_folder = (purchased_folder or _DEFAULT_PURCHASED).strip()
    fabricated_folder = (fabricated_folder or _DEFAULT_FABRICATED).strip()
    assembly_folder = (assembly_folder or _DEFAULT_ASSEMBLY).strip()

    registry = Path(registry_path).expanduser()
    logf = Path(log_path).expanduser()
    work = Path(work_dir).expanduser() if work_dir is not None else registry.parent
    registry.parent.mkdir(parents=True, exist_ok=True)
    logf.parent.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)

    _State.configured = True
    _State.project = project
    _State.root = root.strip("/")
    _State.registry_path = registry
    _State.log_path = logf
    _State.work_dir = work
    _State.purchased_folder = purchased_folder
    _State.fabricated_folder = fabricated_folder
    _State.assembly_folder = assembly_folder


def reset_config() -> None:
    """Clear configuration. Intended for tests."""
    _State.configured = False
    _State.project = ""
    _State.root = ""
    _State.registry_path = None
    _State.log_path = None
    _State.work_dir = None
    _State.purchased_folder = _DEFAULT_PURCHASED
    _State.fabricated_folder = _DEFAULT_FABRICATED
    _State.assembly_folder = _DEFAULT_ASSEMBLY


def is_configured() -> bool:
    """Return True after a successful :func:`configure` call."""
    return _State.configured


def current_config() -> dict[str, Any]:
    """Return a copy of the current configuration values.

    Paths are strings. Folder paths are ``root/folder-name`` with ``/``
    separators, matching Fusion data-folder paths.
    """
    _require()
    assert _State.registry_path is not None
    assert _State.log_path is not None
    assert _State.work_dir is not None
    root = _State.root
    return {
        "project": _State.project,
        "root": root,
        "registry_path": str(_State.registry_path),
        "log_path": str(_State.log_path),
        "work_dir": str(_State.work_dir),
        "purchased_folder": _State.purchased_folder,
        "fabricated_folder": _State.fabricated_folder,
        "assembly_folder": _State.assembly_folder,
        "purchased_path": _join_root(root, _State.purchased_folder),
        "fabricated_path": _join_root(root, _State.fabricated_folder),
        "assembly_path": _join_root(root, _State.assembly_folder),
    }


def folder_paths(
    root: str,
    *,
    purchased_folder: str = _DEFAULT_PURCHASED,
    fabricated_folder: str = _DEFAULT_FABRICATED,
    assembly_folder: str = _DEFAULT_ASSEMBLY,
) -> dict[str, str]:
    """Return purchased, fabricated and assembly folder paths under ``root``.

    This is a pure helper: it does not require :func:`configure`.
    """
    root = (root or "").strip().strip("/")
    return {
        "purchased_path": _join_root(root, purchased_folder),
        "fabricated_path": _join_root(root, fabricated_folder),
        "assembly_path": _join_root(root, assembly_folder),
    }


def log(msg: object) -> None:
    """Append a timestamped line to the configured log file and print it."""
    _require()
    assert _State.log_path is not None
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + str(msg)
    with open(_State.log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(msg)


def registry_file() -> Path:
    """Return the configured registry path."""
    _require()
    assert _State.registry_path is not None
    return _State.registry_path


def project_name() -> str:
    """Return the configured Fusion project name."""
    _require()
    return _State.project
