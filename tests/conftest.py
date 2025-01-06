from __future__ import annotations

import os
from pathlib import Path

import maya.standalone  # type: ignore
import pytest
from maya import cmds  # type: ignore

maya.standalone.initialize(name="python")
from maya_zen_tools import startup  # noqa


SCENES: Path = Path(__file__).absolute().parent / "scenes"


@pytest.fixture(name="poly_sphere")
def get_poly_sphere() -> str:
    """
    Retrieve a scene with a sphere which has known component IDs.
    """
    scene: Path = SCENES / "poly_sphere.ma"
    if not scene.is_file():
        os.makedirs(str(scene.absolute().parent), exist_ok=True)
        cmds.polySphere(
            name="polySphere",
            constructionHistory=False,
        )[0]
        cmds.file(rename=str(scene))
        cmds.file(save=True, type="mayaAscii")
        return "polySphere"
    cmds.file(str(scene), open=True, force=True)
    return "polySphere"


@pytest.fixture(name="poly_plane")
def get_poly_plane() -> str:
    """
    Retrieve a scene with a plane which has known component IDs.
    """
    scene: Path = SCENES / "poly_plane.ma"
    if not scene.is_file():
        os.makedirs(str(scene.absolute().parent), exist_ok=True)
        cmds.polyPlane(
            name="polyPlane",
            subdivisionsX=10,
            subdivisionsY=10,
            constructionHistory=False,
        )[0]
        cmds.delete(
            "polyPlane.f[4:5]",
            "polyPlane.f[14:15]",
        )
        cmds.file(rename=str(scene))
        cmds.file(save=True, type="mayaAscii")
        return "polyPlane"
    cmds.file(str(scene), open=True, force=True)
    return "polyPlane"


@pytest.fixture(name="poly_cylinder")
def get_poly_cylinder() -> str:
    """
    Retrieve a scene with a cylinder which has known component IDs.
    """
    scene: Path = SCENES / "poly_cylinder.ma"
    if not scene.is_file():
        os.makedirs(str(scene.absolute().parent), exist_ok=True)
        cmds.polyCylinder(
            subdivisionsX=20,
            subdivisionsY=20,
            subdivisionsZ=2,
            constructionHistory=False,
            name="polyCylinder",
        )[0]
        cmds.file(rename=str(scene))
        cmds.file(save=True, type="mayaAscii")
        return "polyCylinder"
    cmds.file(str(scene), open=True, force=True)
    return "polyCylinder"
