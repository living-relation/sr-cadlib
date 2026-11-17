# Usage

All snippets below run **inside Fusion** (Fusion MCP `execute_python`, or the script runner). Call `configure()` first.

## Import and configure

```python
import sys
from pathlib import Path
sys.path.insert(0, "/path/to/sr-cadlib")
import sr_cadlib as cad

work = Path("/path/to/build-work")
cad.configure(
    project="MyProject",
    root="Products/Widget",
    registry_path=str(work / "registry.json"),
    log_path=str(work / "build.log"),
    purchased_folder="Purchased Parts",      # optional; default
    fabricated_folder="Fabricated Parts",    # optional; default
    assembly_folder="Subassemblies",         # optional; default
)
# cad.F_PURCH == "Products/Widget/Purchased Parts"
# cad.F_FAB   == "Products/Widget/Fabricated Parts"
# cad.F_ASSY  == "Products/Widget/Subassemblies"
```

## Build and save a part

```python
doc, des = cad.new_design("mm")
comp = des.rootComponent
plate = cad.tbox(0, 0, 0, 80, 40, 6)
cad.bake(comp, [(plate, "Plate")])
cad.holes_through(comp, "z", 0, [(10, 10, 0), (70, 10, 0), (10, 30, 0), (70, 30, 0)], 5.5)
cad.finish(des, comp.bRepBodies, mat=cad.AL, appr=cad.A_AL)
cad.finish_part("plate", doc, des, cad.F_FAB, "Mount Plate", "PLT-001", "Mount plate")
```

`finish_part` writes part number and description, saves into `fold_path` (creates folders as needed), stores `{id, name, pn, desc, folder}` under the key, logs the save, and closes the document unless `close=False`.

## Registry: reopen or insert later

```python
df = cad.reg_file("plate")
# insert into an assembly at the origin, inches:
occ = cad.insert(parent_comp, df, cad.mat_in((0, 0, 0)))
```

`reg_load()` returns the whole dict. `reg_put(key, info)` writes an entry (used by `finish_part`).

## Temporary solids and sketches

```python
# mm: box, cylinder, boolean, then bake into the component
box = cad.tbox(0, 0, 0, 20, 10, 8)
bore = cad.tcyl((10, 5, -1), (10, 5, 9), 3)
cad.tD(box, bore)
cad.bake(comp, [(box, "Block")])

# cm: sketch on a plane normal to Z at z=0, extrude 1 cm
sk = cad.sketch_on(comp, "z", 0, "Profile")
cad.poly(sk, [(0, 0, 0), (2, 0, 0), (2, 1, 0), (0, 1, 0)])
cad.extrude(comp, cad.profiles(sk), 1.0, (0, 0, 1), op="new", name="Pad")
```

## Limits

- `configure()` is required before folder, registry, or log helpers. `ConfigError` is raised otherwise.
- `tbox` / `tcyl` default to millimetres. Sketch and feature helpers with `_cm` in the name use centimetres.
- `new_design` / `finish_part` / `reg_file` / `insert` need a running Fusion session.
- `insert(..., name=)` accepts `name` for compatibility but does not rename the occurrence.
- Keep this library generic. Pass product-specific names only into `configure()` and the calling script, never into the library itself.

A runnable sample (configure + optional Fusion build, closes without saving) is `examples/build_example.py`. The live Fusion smoke test is `dev/fusion_smoke.py`.
