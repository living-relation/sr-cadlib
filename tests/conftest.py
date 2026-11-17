"""Install the Fusion API stub before any test imports sr_cadlib.fusion."""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests import adsk_stub  # noqa: E402

# Present as the 'adsk' package (adsk.core, adsk.fusion) expected by sr_cadlib.
if "adsk" not in sys.modules:
    pkg = types.ModuleType("adsk")
    pkg.core = adsk_stub.core
    pkg.fusion = adsk_stub.fusion
    pkg.doEvents = adsk_stub.doEvents
    sys.modules["adsk"] = pkg
    sys.modules["adsk.core"] = adsk_stub.core  # type: ignore[assignment]
    sys.modules["adsk.fusion"] = adsk_stub.fusion  # type: ignore[assignment]


@pytest.fixture(autouse=True)
def _reset_config():
    from sr_cadlib import reset_config

    reset_config()
    yield
    reset_config()
