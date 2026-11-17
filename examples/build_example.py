"""Example for an agent driving Fusion: configure the library and make a block.

Humans are not expected to write scripts with this library. Run this inside
Fusion (Fusion MCP ``execute_python`` or the script runner). It creates a
scratch design, bakes a 20 x 10 x 8 mm block, sets a part number, and closes
the design without saving. Outside Fusion it only configures and writes the
registry.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import sr_cadlib as cad


def setup(work: Path) -> None:
    cad.configure(
        project="MyProject",
        root="Products/Widget",
        registry_path=work / "registry.json",
        log_path=work / "build.log",
        # Folder names under root are configurable. These are the defaults:
        purchased_folder="Purchased Parts",
        fabricated_folder="Fabricated Parts",
        assembly_folder="Subassemblies",
    )
    print("project:", cad.PROJECT)
    print("purchased folder:", cad.F_PURCH)
    print("fabricated folder:", cad.F_FAB)
    print("assembly folder:", cad.F_ASSY)
    cad.reg_put("sample_block", {"id": "local-only", "name": "Sample Block", "pn": "BLK-001"})
    print("registry keys:", sorted(cad.reg_load()))


def build_block() -> None:
    """Create a temporary block in a scratch Fusion design, then close it."""
    doc, des = cad.new_design("mm")
    body = cad.tbox(0, 0, 0, 20, 10, 8)
    cad.bake(des.rootComponent, [(body, "Block")])
    des.rootComponent.partNumber = "BLK-001"
    des.rootComponent.description = "Sample block"
    cad.log("built sample block in a scratch design")
    doc.close(False)


def main() -> None:
    work = Path(tempfile.mkdtemp(prefix="sr-cadlib-example-"))
    setup(work)
    try:
        import adsk.core  # noqa: F401

        build_block()
        print("closed the scratch design without saving")
    except ImportError:
        print("Fusion is not available; configure and registry steps finished.")
        print("work dir:", work)


if __name__ == "__main__":
    main()
