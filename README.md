> **This is an agent helper tool.** It is for AI agents driving Autodesk Fusion (for example through the Fusion MCP script runner). Humans are not expected to write scripts with it.

# SR CADLib

Agent helper library for Autodesk Fusion API scripting. Use it from the Fusion MCP `execute_python` tool (or Fusion's script runner) when an agent needs to build, place, save, or reopen parts. It is not a Fusion add-in and is not meant for people writing scripts by hand.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Agent quick start

Run this inside Fusion. Replace the clone path, project name, and folder root.

```python
import sys
sys.path.insert(0, "/path/to/sr-cadlib")

import sr_cadlib as cad
from pathlib import Path

work = Path("/path/to/build-work")
cad.configure(
    project="MyProject",
    root="Products/Widget",
    registry_path=str(work / "registry.json"),
    log_path=str(work / "build.log"),
)

doc, des = cad.new_design("mm")
body = cad.tbox(0, 0, 0, 80, 40, 6)          # mm, two opposite corners
cad.bake(des.rootComponent, [(body, "Plate")])
cad.holes_through(des.rootComponent, "z", 0, [(10, 10, 0), (70, 10, 0), (10, 30, 0), (70, 30, 0)], 5.5)
cad.finish(des, des.rootComponent.bRepBodies, mat=cad.AL, appr=cad.A_AL)
cad.finish_part(
    "plate",
    doc,
    des,
    cad.F_FAB,                                 # Products/Widget/Fabricated Parts
    name="Mount Plate",
    pn="PLT-001",
    desc="Mount plate",
)
```

`finish_part` sets the part number and description, saves into the Fusion data folder, records the file id in the registry, and closes the document. A later script reopens or inserts that part with `cad.reg_file("plate")`.

## Configure

Call `configure()` once before any folder, registry, or log helper. There are no built-in project or machine paths.

| Argument | Required | Meaning |
| --- | --- | --- |
| `project` | yes | Fusion data project name |
| `root` | yes | Folder path inside the project, `/` separated |
| `registry_path` | yes | Local JSON file of part key → Fusion file id |
| `log_path` | yes | Local log file `log()` appends to |
| `purchased_folder` | no | Name under `root` (default `Purchased Parts`) → `F_PURCH` |
| `fabricated_folder` | no | Name under `root` (default `Fabricated Parts`) → `F_FAB` |
| `assembly_folder` | no | Name under `root` (default `Subassemblies`) → `F_ASSY` |
| `work_dir` | no | Exposed as `LIBDIR` (default: registry file's directory) |

After `configure()`, `PROJECT`, `ROOT`, `F_PURCH`, `F_FAB`, `F_ASSY`, `REGF`, and `LIBDIR` are live strings.

## Units

Fusion's internal unit is centimetres. Temporary solids (`tbox`, `tcyl`) take millimetres by default (`s=MM`, `MM=0.1`). Sketch and feature helpers whose argument names end in `_cm` take centimetres. `mat_in()` and `rotz180_about()` take inches (`IN=2.54`).

## API

Import: `import sr_cadlib as cad`

**Session:** `configure(...)`, `current_config()`, `is_configured()`, `reset_config()`, `log(msg)`, `project_name()`, `folder_paths(root, ...)`

**Registry:** `reg_put(key, info)`, `reg_load()`, `reg_file(key)` (Fusion data file for a key)

**Documents:** `app()`, `project()`, `folder(path)`, `find_file(fold, name)`, `new_design(units="mm"|"in")`, `save_as(doc, fold, name, desc="")`, `finish_part(key, doc, des, fold_path, name, pn, desc, close=True)`, `wait_complete(getter, timeout=300)`

**Temporary solids (mm):** `tbox(x0,y0,z0,x1,y1,z1)`, `tcyl(p1, p2, r, r2=None)`, `tU(a,b)` union, `tD(a,b)` cut, `tI(a,b)` intersect, `bake(comp, [(body, name), ...])`

**Sketches and features (cm):** `sketch_on(comp, axis, val_cm, name=None)`, `poly(sk, pts)`, `circle(sk, c, r)`, `slot(sk, c1, c2, r)`, `profiles(sk)`, `extrude(comp, profs, dist_cm, dirvec, op="new"|"cut"|"join", name=None, bodies=None)`, `cut_through(comp, profs, name=None, bodies=None)`, `holes_through(comp, axis, plane_val_cm, centers_cm, dia_cm, name=None, bodies=None)`, `combine_cut(comp, target, tools, keep=False, name=None)`, `combine_join(comp, target, tools, name=None)`

**Placement:** `mat(origin_cm, xdir, ydir, zdir)`, `mat_in(origin_in, ...)`, `rotz180_about(xc_in, yc_in)`, `insert(parent_comp, df, m)`

**Materials:** `finish(des, bodies, mat=None, appr=None)` with name lists `STEEL`, `STAINLESS`, `AL`, `IRON`, `PLASTIC`, `A_BLACK`, `A_DARK`, `A_STEEL`, `A_AL`, `A_ANOD_BLK`, `A_BLUE`, `A_ZINC`

**Low-level:** `P`, `V`, `VI`, `TB()`, `m2s`, `base_plane`, `cplane`, `sk_normal`, `OPS`

Copy-paste examples and limits: [docs/usage.md](docs/usage.md). Install for an agent: [docs/install.md](docs/install.md). Full wiki: [docs/README.md](docs/README.md).

## License

[MIT](LICENSE). Copyright (c) 2026 Spark Robotic.
