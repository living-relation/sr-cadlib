"""Tests for unit helpers that can run against the Fusion API stub."""
from __future__ import annotations

from pathlib import Path

import pytest

from sr_cadlib import (
    IN,
    MM,
    P,
    V,
    VI,
    app,
    configure,
    folder,
    mat,
    mat_in,
    new_design,
    project,
    rotz180_about,
    tD,
    tI,
    tU,
    tbox,
    tcyl,
)
from tests import adsk_stub


def test_points_vectors_values():
    p = P(1.5, 2.5, 3.5)
    assert p.asArray() == [1.5, 2.5, 3.5]
    v = V(0, 0, 1)
    assert v.asArray() == [0, 0, 1]
    assert VI(4.2).value == 4.2


def test_vector_math():
    x, y = V(1, 0, 0), V(0, 1, 0)
    z = x.crossProduct(y)
    assert z.asArray() == [0, 0, 1]
    assert x.dotProduct(y) == 0
    assert x.dotProduct(x) == 1


def test_tbox_mm_scale_and_sorted_corners():
    # Corners given out of order, in millimetres; Fusion units are cm.
    body = tbox(10, 20, 30, 0, 0, 0)
    assert body["kind"] == "box"
    obb = body["obb"]
    assert obb.center.asArray() == [0.5, 1.0, 1.5]
    assert obb.length == pytest.approx(10 * MM)
    assert obb.width == pytest.approx(20 * MM)
    assert obb.height == pytest.approx(30 * MM)


def test_tcyl_and_booleans():
    cyl = tcyl((0, 0, 0), (0, 0, 10), 2)
    assert cyl["kind"] == "cyl"
    assert cyl["r1"] == pytest.approx(2 * MM)
    assert cyl["r2"] == pytest.approx(2 * MM)
    assert cyl["p2"].z == pytest.approx(10 * MM)
    cone = tcyl((0, 0, 0), (0, 0, 5), 3, r2=1)
    assert cone["r2"] == pytest.approx(1 * MM)
    a = tbox(0, 0, 0, 10, 10, 10)
    tU(a, cyl)
    tD(a, cone)
    tI(a, cyl)
    kinds = [op[0].name for op in a["ops"]]
    assert kinds == ["union", "difference", "intersection"]


def test_mat_and_mat_in():
    m = mat((1, 2, 3), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    assert m.origin.asArray() == [1, 2, 3]
    mi = mat_in((1, 0, 0))
    assert mi.origin.asArray() == [1 * IN, 0, 0]
    r = rotz180_about(2, 3)
    assert r.origin.asArray() == [2 * 2 * IN, 2 * 3 * IN, 0]
    assert r.axes[0].asArray() == [-1, 0, 0]
    assert r.axes[1].asArray() == [0, -1, 0]
    assert r.axes[2].asArray() == [0, 0, 1]


def test_project_and_folder(tmp_path: Path):
    configure(
        project="MyProject",
        root="Products/Widget",
        registry_path=tmp_path / "registry.json",
        log_path=tmp_path / "build.log",
    )
    adsk_stub._APP.data.dataProjects = [adsk_stub._Project("MyProject")]
    p = project()
    assert p.name == "MyProject"
    fold = folder("Products/Widget/Custom Parts")
    assert fold.name == "Custom Parts"
    # Second call reuses the same folder rather than adding a duplicate.
    again = folder("Products/Widget/Custom Parts")
    assert again is fold
    top = p.rootFolder
    assert [c.name for c in top.dataFolders] == ["Products"]
    assert [c.name for c in top.dataFolders._items[0].dataFolders] == ["Widget"]


def test_project_missing(tmp_path: Path):
    configure(
        project="Missing",
        root="Products/Widget",
        registry_path=tmp_path / "registry.json",
        log_path=tmp_path / "build.log",
    )
    adsk_stub._APP.data.dataProjects = [adsk_stub._Project("Other")]
    with pytest.raises(Exception, match="project not found"):
        project()


def test_new_design_mm_and_inch():
    doc, des = new_design("mm")
    assert des.fusionUnitsManager.distanceDisplayUnits.name == "mm"
    assert des.designType.name == "parametric"
    assert app() is adsk_stub._APP
    doc2, des2 = new_design("in")
    assert des2.fusionUnitsManager.distanceDisplayUnits.name == "in"
