from __future__ import annotations

import os
from pathlib import Path

import maya.standalone  # type: ignore
import pytest

from maya_zen_tools.loft import _iter_contiguous_edges

maya.standalone.initialize(name="python")
from maya import cmds  # type: ignore  # noqa: E402

from maya_zen_tools import startup  # noqa

SCENE: Path = Path(__file__).absolute().parent / "scenes" / "test_loft.ma"


def create_scene() -> None:
    """
    This creates or opens a scene for testing `maya_zen_tools.loop`.
    Once created, this scene is retained in order to maintain a known
    pattern of vertex IDs. If the scene is deleted, this function will recreate
    it, but all vertex IDs will need to be checked, and most will need
    replaced. The face IDs below may also need to be adjusted.
    """
    if not SCENE.is_file():
        os.makedirs(str(SCENE.absolute().parent), exist_ok=True)
        cmds.polySphere(
            name="polySphere",
            constructionHistory=False,
        )[0]
        cmds.file(rename=str(SCENE))
        cmds.file(save=True, type="mayaAscii")
        return
    cmds.file(str(SCENE), open=True, force=True)


def test_iter_contiguous_edges() -> None:
    """
    Test `flood_select`.
    """
    create_scene()
    assert (
        len(
            tuple(
                _iter_contiguous_edges(
                    "polySphere.e[293]",
                    "polySphere.e[294]",
                    "polySphere.e[295]",
                    "polySphere.e[296]",
                    "polySphere.e[297]",
                    "polySphere.e[298]",
                    "polySphere.e[299]",
                    "polySphere.e[153]",
                    "polySphere.e[154]",
                    "polySphere.e[155]",
                    "polySphere.e[156]",
                    "polySphere.e[157]",
                    "polySphere.e[158]",
                    "polySphere.e[159]",
                    "polySphere.e[93]",
                    "polySphere.e[94]",
                    "polySphere.e[95]",
                    "polySphere.e[96]",
                    "polySphere.e[97]",
                    "polySphere.e[98]",
                    "polySphere.e[99]",
                )
            )
        )
        == 3
    )


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
