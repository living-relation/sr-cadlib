"""The library tree must stay generic: no customer or product project names."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check  # noqa: E402


def test_tree_has_no_forbidden_project_names():
    errors = [e for e in check.scan() if "forbidden project name" in e]
    assert errors == []
