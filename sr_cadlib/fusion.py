"""Fusion API helpers for points, solids, sketches, features, materials and saves.

These functions require Autodesk Fusion (the ``adsk`` module). Unit tests mock
that module. Lengths passed to the temporary-solid helpers are millimetres by
default (they are multiplied by :data:`MM`). Sketch and feature helpers that
take an explicit ``_cm`` argument use Fusion's internal centimetre units.
"""
from __future__ import annotations

import time
from typing import Any, Callable, Iterable, Sequence

import adsk.core
import adsk.fusion

from .config import IN, MM, log, project_name
from .registry import reg_put


def app() -> Any:
    """Return the running Fusion application."""
    return adsk.core.Application.get()


def P(x: float, y: float, z: float) -> Any:
    """Create a Fusion 3D point."""
    return adsk.core.Point3D.create(x, y, z)


def V(x: float, y: float, z: float) -> Any:
    """Create a Fusion 3D vector."""
    return adsk.core.Vector3D.create(x, y, z)


def VI(v: float) -> Any:
    """Create a Fusion real value input."""
    return adsk.core.ValueInput.createByReal(v)


def project() -> Any:
    """Return the configured Fusion data project, or raise if it is not found."""
    name = project_name()
    for p in app().data.dataProjects:
        if p.name == name:
            return p
    raise Exception("project not found")


def folder(path: str) -> Any:
    """Return (and create if needed) a data folder under the project root.

    ``path`` uses ``/`` separators, relative to the project root.
    """
    f = project().rootFolder
    for nm in path.split("/"):
        if not nm:
            continue
        sub = None
        for d in f.dataFolders:
            if d.name == nm:
                sub = d
                break
        if sub is None:
            sub = f.dataFolders.add(nm)
        f = sub
    return f


def find_file(fold: Any, name: str) -> Any | None:
    """Return the data file named ``name`` in ``fold``, or None."""
    for df in fold.dataFiles:
        if df.name == name:
            return df
    return None


def new_design(units: str = "mm") -> tuple[Any, Any]:
    """Create a new parametric Fusion design in millimetres or inches."""
    doc = app().documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    des.designType = adsk.fusion.DesignTypes.ParametricDesignType
    um = des.fusionUnitsManager
    um.distanceDisplayUnits = (
        adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        if units == "mm"
        else adsk.fusion.DistanceUnits.InchDistanceUnits
    )
    return doc, des


def wait_complete(getter: Callable[[], Any], timeout: float = 300) -> Any | None:
    """Poll ``getter`` until it returns a complete Fusion data file, or time out."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        adsk.doEvents()
        try:
            df = getter()
            if df is not None and df.isComplete:
                return df
        except Exception:
            pass
        time.sleep(0.3)
    return None


def save_as(doc: Any, fold: Any, name: str, desc: str = "") -> Any:
    """Save ``doc`` into ``fold`` and wait until the data file is complete."""
    ok = doc.saveAs(name, fold, desc, "")
    if not ok:
        raise Exception("saveAs failed for " + name)
    df = wait_complete(lambda: doc.dataFile)
    if df is None:
        raise Exception("dataFile not complete for " + name)
    return df


def finish_part(
    key: str,
    doc: Any,
    des: Any,
    fold_path: str,
    name: str,
    pn: str,
    desc: str,
    close: bool = True,
) -> Any:
    """Set part number and description, save, register the file, and optionally close."""
    root = des.rootComponent
    root.partNumber = pn
    root.description = desc
    df = save_as(doc, folder(fold_path), name, desc)
    reg_put(key, {"id": df.id, "name": name, "pn": pn, "desc": desc, "folder": fold_path})
    log("SAVED %s -> %s (%s)" % (key, name, df.id))
    if close:
        doc.close(False)
    return df


# ---------------- materials / appearance ----------------
STEEL = ["Steel", "Steel, Mild", "Steel AISI 1020 102 HR", "Steel, Cast"]
STAINLESS = ["Stainless Steel", "Steel, Stainless", "Stainless Steel AISI 304"]
AL = ["Aluminum 6061", "Aluminum, 6061-T6", "Aluminum"]
IRON = ["Iron, Cast", "Iron, Gray", "Steel"]
PLASTIC = ["ABS Plastic", "Plastic", "Nylon 6/6"]
A_BLACK = ["Paint - Enamel Glossy (Black)", "Paint - Enamel Matte (Black)", "Plastic - Matte (Black)"]
A_DARK = ["Plastic - Matte (Black)", "Plastic - Glossy (Black)"]
A_STEEL = ["Steel - Satin", "Stainless Steel - Satin"]
A_AL = ["Aluminum - Satin", "Aluminum - Brushed", "Aluminum - Polished"]
A_ANOD_BLK = ["Aluminum - Anodized Glossy (Blue)", "Aluminum - Anodized Rough (Blue)", "Aluminum - Satin"]
A_BLUE = ["Paint - Enamel Glossy (Blue)", "Plastic - Glossy (Blue)"]
A_ZINC = ["Zinc", "Steel - Galvanized", "Steel - Satin"]


def _lib(kind: str) -> Any:
    """Return the Fusion material or appearance library, or None."""
    names = (
        ["Fusion Material Library", "Fusion 360 Material Library"]
        if kind == "mat"
        else ["Fusion Appearance Library", "Fusion 360 Appearance Library"]
    )
    for n in names:
        lib = app().materialLibraries.itemByName(n)
        if lib:
            return lib
    return None


def get_material(opts: Sequence[str]) -> Any | None:
    """Return the first material whose name is in ``opts``, or None."""
    lib = _lib("mat")
    if lib is None:
        return None
    for n in opts:
        try:
            m = lib.materials.itemByName(n)
        except Exception:
            m = None
        if m:
            return m
    return None


def get_appearance(des: Any, opts: Sequence[str]) -> Any | None:
    """Return the first appearance whose name is in ``opts``, copying it into ``des`` if needed."""
    for n in opts:
        try:
            ap = des.appearances.itemByName(n)
        except Exception:
            ap = None
        if ap:
            return ap
    lib = _lib("app")
    if lib is None:
        return None
    for n in opts:
        try:
            la = lib.appearances.itemByName(n)
        except Exception:
            la = None
        if la:
            try:
                return des.appearances.addByCopy(la, n)
            except Exception:
                return la
    return None


def finish(des: Any, bodies: Iterable[Any], mat: Sequence[str] | None = None, appr: Sequence[str] | None = None) -> None:
    """Apply a material and/or appearance name list to each body."""
    m = get_material(mat) if mat else None
    ap = get_appearance(des, appr) if appr else None
    for b in bodies:
        if b is None:
            continue
        if m:
            try:
                b.material = m
            except Exception:
                pass
        if ap:
            try:
                b.appearance = ap
            except Exception:
                pass


# ---------------- temporary BRep ----------------
def TB() -> Any:
    """Return Fusion's temporary B-rep manager."""
    return adsk.fusion.TemporaryBRepManager.get()


def tbox(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float, s: float = MM) -> Any:
    """Create a temporary box from two opposite corners, scaled by ``s`` (default mm)."""
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    za, zb = sorted((z0, z1))
    obb = adsk.core.OrientedBoundingBox3D.create(
        P((xa + xb) / 2 * s, (ya + yb) / 2 * s, (za + zb) / 2 * s),
        V(1, 0, 0),
        V(0, 1, 0),
        (xb - xa) * s,
        (yb - ya) * s,
        (zb - za) * s,
    )
    return TB().createBox(obb)


def tcyl(p1: Sequence[float], p2: Sequence[float], r: float, r2: float | None = None, s: float = MM) -> Any:
    """Create a temporary cylinder or cone between two points, scaled by ``s`` (default mm)."""
    return TB().createCylinderOrCone(
        P(p1[0] * s, p1[1] * s, p1[2] * s),
        r * s,
        P(p2[0] * s, p2[1] * s, p2[2] * s),
        (r if r2 is None else r2) * s,
    )


def tU(a: Any, b: Any) -> Any:
    """Union temporary body ``b`` into ``a`` and return ``a``."""
    TB().booleanOperation(a, b, adsk.fusion.BooleanTypes.UnionBooleanType)
    return a


def tD(a: Any, b: Any) -> Any:
    """Subtract temporary body ``b`` from ``a`` and return ``a``."""
    TB().booleanOperation(a, b, adsk.fusion.BooleanTypes.DifferenceBooleanType)
    return a


def tI(a: Any, b: Any) -> Any:
    """Intersect temporary body ``b`` with ``a`` and return ``a``."""
    TB().booleanOperation(a, b, adsk.fusion.BooleanTypes.IntersectionBooleanType)
    return a


def bake(comp: Any, items: Iterable[tuple[Any, str]]) -> list[Any]:
    """Add named temporary bodies to ``comp`` as a base feature and return those bodies."""
    bf = comp.features.baseFeatures.add()
    bf.startEdit()
    for b, n in items:
        nb = comp.bRepBodies.add(b, bf)
        nb.name = n
    bf.finishEdit()
    bf.name = "Envelope geometry"
    return [comp.bRepBodies.itemByName(n) for b, n in items]


# ---------------- transforms ----------------
def mat(origin_cm: Sequence[float], xdir: Sequence[float], ydir: Sequence[float], zdir: Sequence[float]) -> Any:
    """Build a placement matrix from an origin in centimetres and three axis directions."""
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(P(*origin_cm), V(*xdir), V(*ydir), V(*zdir))
    return m


def mat_in(
    origin_in: Sequence[float],
    xdir: Sequence[float] = (1, 0, 0),
    ydir: Sequence[float] = (0, 1, 0),
    zdir: Sequence[float] = (0, 0, 1),
) -> Any:
    """Build a placement matrix from an origin in inches and three axis directions."""
    return mat([v * IN for v in origin_in], xdir, ydir, zdir)


def rotz180_about(xc_in: float, yc_in: float) -> Any:
    """Return a 180 degree rotation about the vertical axis through ``(xc_in, yc_in)`` inches."""
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(P(2 * xc_in * IN, 2 * yc_in * IN, 0), V(-1, 0, 0), V(0, -1, 0), V(0, 0, 1))
    return m


def insert(parent_comp: Any, df: Any, m: Any, name: str | None = None) -> Any:
    """Insert data file ``df`` into ``parent_comp`` with transform ``m``, and ground it.

    ``name`` is accepted for compatibility and is not applied; Fusion names the
    occurrence from the inserted file.
    """
    occ = parent_comp.occurrences.addByInsert(df, m, True)
    if occ is None:
        raise Exception("insert failed")
    try:
        occ.isGrounded = True
    except Exception:
        pass
    return occ


# ---------------- parametric sketch helpers (model coords in cm) ----------------
def base_plane(comp: Any, which: str) -> Any:
    """Return the XY, XZ or YZ construction plane of ``comp``."""
    return {"xy": comp.xYConstructionPlane, "xz": comp.xZConstructionPlane, "yz": comp.yZConstructionPlane}[which]


def cplane(comp: Any, base: Any, off_cm: float) -> Any:
    """Create a construction plane offset from ``base`` by ``off_cm`` centimetres."""
    ci = comp.constructionPlanes.createInput()
    ci.setByOffset(base, VI(off_cm))
    return comp.constructionPlanes.add(ci)


def sketch_on(comp: Any, axis: str, val_cm: float, name: str | None = None) -> Any:
    """Start a sketch on a plane normal to ``axis`` at ``val_cm`` centimetres."""
    which = {"z": "xy", "y": "xz", "x": "yz"}[axis]
    bp = base_plane(comp, which)
    if abs(val_cm) < 1e-9:
        pl = bp
    else:
        pl = cplane(comp, bp, val_cm)
        idx = {"x": 0, "y": 1, "z": 2}[axis]
        if abs(pl.geometry.origin.asArray()[idx] - val_cm) > 1e-6:
            pl.deleteMe()
            pl = cplane(comp, bp, -val_cm)
        try:
            pl.isLightBulbOn = False
        except Exception:
            pass
    sk = comp.sketches.add(pl)
    if name:
        sk.name = name
    return sk


def m2s(sk: Any, x: float, y: float, z: float) -> Any:
    """Convert a model-space point in centimetres into the sketch's 2D space."""
    return sk.modelToSketchSpace(P(x, y, z))


def poly(sk: Any, pts: Sequence[Sequence[float]]) -> None:
    """Draw a closed polyline through model-space points (centimetres) on ``sk``."""
    ls = sk.sketchCurves.sketchLines
    sp = [m2s(sk, *p) for p in pts]
    first = ls.addByTwoPoints(sp[0], sp[1])
    prev = first
    for i in range(2, len(sp)):
        prev = ls.addByTwoPoints(prev.endSketchPoint, sp[i])
    ls.addByTwoPoints(prev.endSketchPoint, first.startSketchPoint)


def circle(sk: Any, c: Sequence[float], r: float) -> Any:
    """Draw a circle on ``sk`` with model-space centre ``c`` (cm) and radius ``r`` (cm)."""
    return sk.sketchCurves.sketchCircles.addByCenterRadius(m2s(sk, *c), r)


def slot(sk: Any, c1: Sequence[float], c2: Sequence[float], r: float) -> None:
    """Draw an obround slot of radius ``r`` (cm) between model-space centres ``c1`` and ``c2``."""
    a = m2s(sk, *c1)
    b = m2s(sk, *c2)
    dx, dy = b.x - a.x, b.y - a.y
    L = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / L, dy / L
    nx, ny = -uy * r, ux * r
    ls = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    p1 = adsk.core.Point3D.create(a.x + nx, a.y + ny, 0)
    p2 = adsk.core.Point3D.create(b.x + nx, b.y + ny, 0)
    p3 = adsk.core.Point3D.create(b.x - nx, b.y - ny, 0)
    p4 = adsk.core.Point3D.create(a.x - nx, a.y - ny, 0)
    l1 = ls.addByTwoPoints(p1, p2)
    l2 = ls.addByTwoPoints(p3, p4)
    import math

    arcs.addByCenterStartSweep(adsk.core.Point3D.create(b.x, b.y, 0), l1.endSketchPoint, -math.pi)
    arcs.addByCenterStartSweep(adsk.core.Point3D.create(a.x, a.y, 0), l2.endSketchPoint, -math.pi)


def profiles(sk: Any) -> list[Any]:
    """Return all profiles on sketch ``sk``."""
    return [sk.profiles.item(i) for i in range(sk.profiles.count)]


def sk_normal(sk: Any) -> Any:
    """Return the sketch plane normal as a vector."""
    return sk.xDirection.crossProduct(sk.yDirection)


OPS = {
    "new": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    "cut": adsk.fusion.FeatureOperations.CutFeatureOperation,
    "join": adsk.fusion.FeatureOperations.JoinFeatureOperation,
}


def extrude(
    comp: Any,
    profs: Sequence[Any],
    dist_cm: float,
    dirvec: Sequence[float],
    op: str = "new",
    name: str | None = None,
    bodies: list[Any] | None = None,
) -> Any:
    """Extrude ``profs`` by ``dist_cm`` centimetres in direction ``dirvec``."""
    coll = adsk.core.ObjectCollection.create()
    for p in profs:
        coll.add(p)
    ex = comp.features.extrudeFeatures
    inp = ex.createInput(coll, OPS[op])
    n = sk_normal(profs[0].parentSketch)
    d = V(*dirvec)
    dirn = (
        adsk.fusion.ExtentDirections.PositiveExtentDirection
        if n.dotProduct(d) >= 0
        else adsk.fusion.ExtentDirections.NegativeExtentDirection
    )
    inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(VI(abs(dist_cm))), dirn)
    if bodies:
        inp.participantBodies = bodies
    f = ex.add(inp)
    if name:
        f.name = name
    return f


def cut_through(comp: Any, profs: Sequence[Any], name: str | None = None, bodies: list[Any] | None = None) -> Any:
    """Cut all the way through with ``profs``, trying symmetric then each direction."""
    coll = adsk.core.ObjectCollection.create()
    for p in profs:
        coll.add(p)
    ex = comp.features.extrudeFeatures
    f = None
    err: Exception | None = None
    for dirn in (
        adsk.fusion.ExtentDirections.SymmetricExtentDirection,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    ):
        try:
            inp = ex.createInput(coll, OPS["cut"])
            inp.setAllExtent(dirn)
            if bodies:
                inp.participantBodies = bodies
            f = ex.add(inp)
            break
        except Exception as e:
            err = e
            f = None
    if f is None:
        raise err
    if name:
        f.name = name
    return f


def holes_through(
    comp: Any,
    axis: str,
    plane_val_cm: float,
    centers_cm: Sequence[Sequence[float]],
    dia_cm: float,
    name: str | None = None,
    bodies: list[Any] | None = None,
) -> Any:
    """Cut through-holes of diameter ``dia_cm`` at ``centers_cm`` on a plane normal to ``axis``."""
    sk = sketch_on(comp, axis, plane_val_cm, (name or "Holes") + " sketch")
    for c in centers_cm:
        circle(sk, c, dia_cm / 2)
    return cut_through(comp, profiles(sk), name, bodies)


def combine_cut(comp: Any, target: Any, tools: Iterable[Any], keep: bool = False, name: str | None = None) -> Any:
    """Cut ``tools`` from ``target``. ``keep`` leaves the tool bodies in place."""
    coll = adsk.core.ObjectCollection.create()
    for t in tools:
        coll.add(t)
    ci = comp.features.combineFeatures.createInput(target, coll)
    ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    ci.isKeepToolBodies = keep
    f = comp.features.combineFeatures.add(ci)
    if name:
        f.name = name
    return f


def combine_join(comp: Any, target: Any, tools: Iterable[Any], name: str | None = None) -> Any:
    """Join ``tools`` onto ``target`` and discard the tool bodies."""
    coll = adsk.core.ObjectCollection.create()
    for t in tools:
        coll.add(t)
    ci = comp.features.combineFeatures.createInput(target, coll)
    ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    ci.isKeepToolBodies = False
    f = comp.features.combineFeatures.add(ci)
    if name:
        f.name = name
    return f
