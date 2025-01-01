from __future__ import annotations

import maya.standalone  # type: ignore
import pytest

maya.standalone.initialize(name="python")
from maya import cmds  # type: ignore  # noqa: E402

from maya_zen_tools.loop import (  # noqa: E402
    DistributionType,
    curve_distribute_vertices,
)


def test_curve_distribute_between_vertices_4() -> None:
    """
    Test `curve_distribute_vertices` with a 4 vertex selection.
    """
    poly_plane_uniform: str = cmds.polyPlane(
        subdivisionsX=10, subdivisionsY=10, constructionHistory=False
    )[0]
    cmds.move(0, 0.3, 0, f"{poly_plane_uniform}.vtx[38]", relative=True)
    cmds.move(0, 0.4, 0, f"{poly_plane_uniform}.vtx[82]", relative=True)
    selection: tuple[str, ...] = (
        f"{poly_plane_uniform}.vtx[5]",
        f"{poly_plane_uniform}.vtx[38]",
        f"{poly_plane_uniform}.vtx[82]",
        f"{poly_plane_uniform}.vtx[115]",
    )
    cmds.select(*selection)
    curve_distribute_vertices()
    # Check to see that the selection has been restored
    assert set(cmds.ls(selection=True, flatten=True)) == set(selection)
    # Check to see that vertices between the selected have moved
    vertex_id: int
    for vertex_id in (16, 60, 104):
        assert (
            cmds.pointPosition(f"{poly_plane_uniform}.vtx[{vertex_id}]")[1]
            != 0
        )
    # Test a proportional distribution to make sure it is different
    poly_plane_proportional: str = cmds.polyPlane(
        subdivisionsX=10, subdivisionsY=10, constructionHistory=False
    )[0]
    cmds.move(0, 0.3, 0, f"{poly_plane_proportional}.vtx[38]", relative=True)
    cmds.move(0, 0.4, 0, f"{poly_plane_proportional}.vtx[82]", relative=True)
    cmds.select(
        f"{poly_plane_proportional}.vtx[5]",
        f"{poly_plane_proportional}.vtx[38]",
        f"{poly_plane_proportional}.vtx[82]",
        f"{poly_plane_proportional}.vtx[115]",
    )
    curve_distribute_vertices(distribution_type=DistributionType.PROPORTIONAL)
    for vertex_id in (16, 60, 104):
        assert cmds.pointPosition(
            f"{poly_plane_uniform}.vtx[{vertex_id}]"
        ) != cmds.pointPosition(f"{poly_plane_proportional}.vtx[{vertex_id}]")


def test_curve_distribute_between_vertices_3() -> None:
    """
    Test `curve_distribute_vertices` with a 3 vertex selection.
    """
    poly_plane_uniform: str = cmds.polyPlane(
        subdivisionsX=10, subdivisionsY=10, constructionHistory=False
    )[0]
    cmds.move(0, 0.3, 0, f"{poly_plane_uniform}.vtx[38]", relative=True)
    selection: tuple[str, ...] = (
        f"{poly_plane_uniform}.vtx[5]",
        f"{poly_plane_uniform}.vtx[38]",
        f"{poly_plane_uniform}.vtx[115]",
    )
    cmds.select(*selection)
    curve_distribute_vertices()
    # Check to see that the selection has been restored
    assert set(cmds.ls(selection=True, flatten=True)) == set(selection)
    # Check to see that vertices between the selected have moved
    vertex_id: int
    for vertex_id in (16, 60, 104):
        assert (
            cmds.pointPosition(f"{poly_plane_uniform}.vtx[{vertex_id}]")[1]
            != 0
        )
    # Test a proportional distribution to make sure it is different
    poly_plane_proportional: str = cmds.polyPlane(
        subdivisionsX=10, subdivisionsY=10, constructionHistory=False
    )[0]
    cmds.move(0, 0.3, 0, f"{poly_plane_proportional}.vtx[38]", relative=True)
    cmds.select(
        f"{poly_plane_proportional}.vtx[5]",
        f"{poly_plane_proportional}.vtx[38]",
        f"{poly_plane_proportional}.vtx[115]",
    )
    curve_distribute_vertices(distribution_type=DistributionType.PROPORTIONAL)
    for vertex_id in (16, 60, 104):
        assert cmds.pointPosition(
            f"{poly_plane_uniform}.vtx[{vertex_id}]"
        ) != cmds.pointPosition(f"{poly_plane_proportional}.vtx[{vertex_id}]")


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
