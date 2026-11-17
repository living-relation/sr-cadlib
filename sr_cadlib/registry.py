"""Local JSON registry of saved Fusion files, keyed by a short name."""
from __future__ import annotations

import json
from typing import Any

from .config import registry_file


def reg_load() -> dict[str, Any]:
    """Return the registry dict, or an empty dict if the file does not exist."""
    path = registry_file()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def reg_put(key: str, info: dict[str, Any]) -> None:
    """Create or replace the entry for ``key`` and write the registry."""
    data = reg_load()
    data[key] = info
    path = registry_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


def reg_file(key: str) -> Any:
    """Return the Fusion data file for a registered key.

    Looks up ``id`` in the registry and calls ``app().data.findFileById``.
    Raises ``Exception`` if the key or the Fusion file is missing.
    """
    from .fusion import app

    data = reg_load()
    if key not in data:
        raise Exception("registry missing " + key)
    df = app().data.findFileById(data[key]["id"])
    if df is None:
        raise Exception("file not found for " + key)
    return df
