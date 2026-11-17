"""Live Fusion smoke test for SR CADLib.

Takes the machine Fusion lock first (see the workstation fusion-lock script).
Creates a scratch design, bakes a small block with the library, then closes
the design without saving. Never touches other open documents.

Run from a machine that has Fusion and this repository on PYTHONPATH:

    python dev/fusion_smoke.py

Or execute the file with Fusion's script runner after putting this repo on
the script path.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import sr_cadlib as cad


def run(_context: str = "") -> None:
    work = Path(tempfile.mkdtemp(prefix="sr-cadlib-smoke-"))
    cad.configure(
        project="SmokeTest",
        root="Smoke/Test",
        registry_path=work / "registry.json",
        log_path=work / "build.log",
    )
    doc, des = cad.new_design("mm")
    body = cad.tbox(0, 0, 0, 20, 10, 8)
    baked = cad.bake(des.rootComponent, [(body, "SmokeBlock")])
    if not baked or baked[0] is None:
        raise RuntimeError("bake did not produce a body")
    des.rootComponent.partNumber = "SMOKE-001"
    des.rootComponent.description = "CADLib smoke block"
    cad.log("smoke: built and will close without saving")
    doc.close(False)
    print("sr-cadlib smoke: PASS")
    print("work dir:", work)


if __name__ == "__main__":
    run()
