"""Public-repo hygiene: no machine paths in the library tree."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check  # noqa: E402


def test_tree_has_no_machine_paths_or_secrets():
    errors = [e for e in check.scan() if "forbidden project name" not in e]
    assert errors == []
