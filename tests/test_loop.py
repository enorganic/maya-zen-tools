from __future__ import annotations

import os
from pathlib import Path

import maya.standalone  # type: ignore
import pytest

maya.standalone.initialize(name="python")
from maya import cmds  # type: ignore  # noqa: E402

from maya_zen_tools import startup  # noqa
from maya_zen_tools.loop import (  # noqa: E402
    curve_distribute_vertices,
    select_edges_between_vertices,
)
from maya_zen_tools.options import DistributionType  # noqa: E402

SCENE: Path = Path(__file__).absolute().parent / "scenes" / "test_loop.ma"


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
        cmds.file(rename=str(SCENE))
        cmds.file(save=True, type="mayaAscii")
    cmds.file(str(SCENE), open=True, force=True)


def test_select_edges_between_vertices() -> None:
    """
    This tests `maya_zen_tools.loop.select_edges_between_vertices` by
    selecting vertices along a known contiguous edge loop segment, will
    should produce identical selections each time, given the same inputs.
    """
    create_scene()
    assert cmds.selectPref(trackSelectionOrder=True, query=True)
    cmds.select(clear=True)
    cmds.select("polyPlane.vtx[20]")
    cmds.select("polyPlane.vtx[30]", add=True)
    assert select_edges_between_vertices(use_selection_order=True) == (
        "polyPlane.e[36]",
        "polyPlane.e[38]",
        "polyPlane.e[40]",
        "polyPlane.e[42]",
        "polyPlane.e[44]",
        "polyPlane.e[46]",
        "polyPlane.e[48]",
        "polyPlane.e[50]",
        "polyPlane.e[52]",
        "polyPlane.e[54]",
    )
    assert cmds.ls(flatten=True, orderedSelection=True) == [
        "polyPlane.e[36]",
        "polyPlane.e[38]",
        "polyPlane.e[40]",
        "polyPlane.e[42]",
        "polyPlane.e[44]",
        "polyPlane.e[46]",
        "polyPlane.e[48]",
        "polyPlane.e[50]",
        "polyPlane.e[52]",
        "polyPlane.e[54]",
    ]
    cmds.select("polyPlane.vtx[113]", add=True)
    cmds.select("polyPlane.vtx[25]", add=True)
    assert select_edges_between_vertices(use_selection_order=True) == (
        "polyPlane.e[194]",
        "polyPlane.e[173]",
        "polyPlane.e[152]",
        "polyPlane.e[131]",
        "polyPlane.e[110]",
        "polyPlane.e[89]",
        "polyPlane.e[68]",
        "polyPlane.e[47]",
    )
    assert cmds.ls(flatten=True, orderedSelection=True) == [
        "polyPlane.e[36]",
        "polyPlane.e[38]",
        "polyPlane.e[40]",
        "polyPlane.e[42]",
        "polyPlane.e[44]",
        "polyPlane.e[46]",
        "polyPlane.e[48]",
        "polyPlane.e[50]",
        "polyPlane.e[52]",
        "polyPlane.e[54]",
        "polyPlane.e[47]",
        "polyPlane.e[68]",
        "polyPlane.e[89]",
        "polyPlane.e[110]",
        "polyPlane.e[131]",
        "polyPlane.e[152]",
        "polyPlane.e[173]",
        "polyPlane.e[194]",
    ]


def test_curve_distribute_between_vertices_4() -> None:
    """
    This tests `maya_zen_tools.loop.curve_distribute_vertices` by moving two
    vertices along an edge loop, then selecting those two vertices as well as
    the end vertices on the loop and creating a curve from this 4 vertex
    selection, in the order we want the curve to progress. The plane is also
    duplicated in order to compare distribution types.
    """
    poly_plane_2: str = cmds.duplicate("polyPlane")[0]
    cmds.move(0, 0.3, 0, "polyPlane.vtx[61]", relative=True)
    cmds.move(0, 0.4, 0, "polyPlane.vtx[56]", relative=True)
    selection: tuple[str, ...] = (
        "polyPlane.vtx[63]",
        "polyPlane.vtx[61]",
        "polyPlane.vtx[56]",
        "polyPlane.vtx[53]",
    )
    cmds.select(*selection)
    curve_distribute_vertices(use_selection_order=True)
    # Check to see that the selection has been restored
    assert set(cmds.ls(selection=True, flatten=True)) == set(selection)
    # Check to see that vertices between the selected have moved
    vertex_id: int
    for vertex_id in (54, 58, 62):
        assert (
            cmds.pointPosition(f"polyPlane.vtx[{vertex_id}]")[1] != 0
        ), vertex_id
    # Test a proportional distribution to make sure it is different
    cmds.move(0, 0.3, 0, f"{poly_plane_2}.vtx[61]", relative=True)
    cmds.move(0, 0.4, 0, f"{poly_plane_2}.vtx[56]", relative=True)
    cmds.select(
        f"{poly_plane_2}.vtx[63]",
        f"{poly_plane_2}.vtx[61]",
        f"{poly_plane_2}.vtx[56]",
        f"{poly_plane_2}.vtx[53]",
    )
    curve_distribute_vertices(
        use_selection_order=True,
        distribution_type=DistributionType.PROPORTIONAL,
    )
    for vertex_id in (54, 58, 62):
        assert cmds.pointPosition(
            f"polyPlane.vtx[{vertex_id}]"
        ) != cmds.pointPosition(f"{poly_plane_2}.vtx[{vertex_id}]"), vertex_id


def test_curve_distribute_between_vertices_3() -> None:
    """
    This tests `maya_zen_tools.loop.curve_distribute_vertices` by moving one
    vertex along an edge loop, then selecting that vertex as well as
    the end vertices on the loop and creating a curve from this 3 vertex
    selection, in the order we want the curve to progress. The plane is also
    duplicated in order to compare distribution types. We do this for a 3
    vertex selection specifically because the curve created for 3 vertices
    uses an arc node rather than a loft.
    """
    create_scene()
    cmds.move(0, 0.3, 0, "polyPlane.vtx[59]", relative=True)
    selection: tuple[str, ...] = (
        "polyPlane.vtx[63]",
        "polyPlane.vtx[59]",
        "polyPlane.vtx[53]",
    )
    cmds.select(clear=True)
    vertex: str
    for vertex in selection:
        cmds.select(vertex, add=True)
    curve_distribute_vertices(
        use_selection_order=True, distribution_type=DistributionType.UNIFORM
    )
    # Check to see that the selection has been restored
    assert set(cmds.ls(selection=True, flatten=True)) == set(selection)
    # Check to see that vertices between the selected have moved
    vertex_id: int
    for vertex_id in (61, 56):
        assert cmds.pointPosition(f"polyPlane.vtx[{vertex_id}]")[1] != 0
    # Test a proportional distribution to make sure it is different
    poly_plane_2: str = cmds.duplicate("polyPlane")[0]
    cmds.move(0, 0.3, 0, f"{poly_plane_2}.vtx[59]", relative=True)
    cmds.select(clear=True)
    for vertex in (
        f"{poly_plane_2}.vtx[63]",
        f"{poly_plane_2}.vtx[59]",
        f"{poly_plane_2}.vtx[53]",
    ):
        cmds.select(vertex, add=True)
    curve_distribute_vertices(
        use_selection_order=True,
        distribution_type=DistributionType.PROPORTIONAL,
    )
    for vertex_id in (61, 56):
        assert cmds.pointPosition(
            f"polyPlane.vtx[{vertex_id}]"
        ) != cmds.pointPosition(f"{poly_plane_2}.vtx[{vertex_id}]")


def test_select_edges_between_vertices_closed() -> None:
    """
    This tests `maya_zen_tools.loop.select_edges_between_vertices` using
    corner vertices for the selection.
    """
    create_scene()
    selected_vertices: tuple[str, ...] = (
        "polyPlane.vtx[118]",
        "polyPlane.vtx[108]",
        "polyPlane.vtx[0]",
        "polyPlane.vtx[4]",
        "polyPlane.vtx[24]",
        "polyPlane.vtx[26]",
        "polyPlane.vtx[5]",
        "polyPlane.vtx[9]",
    )
    cmds.select(clear=True)
    vertex: str
    for vertex in selected_vertices:
        cmds.select(vertex, add=True)
    # Get a tuple of the vertices between
    assert select_edges_between_vertices(
        use_selection_order=True, close=True
    ) == (
        "polyPlane.e[213]",
        "polyPlane.e[212]",
        "polyPlane.e[211]",
        "polyPlane.e[210]",
        "polyPlane.e[209]",
        "polyPlane.e[208]",
        "polyPlane.e[207]",
        "polyPlane.e[206]",
        "polyPlane.e[205]",
        "polyPlane.e[204]",
        "polyPlane.e[184]",
        "polyPlane.e[163]",
        "polyPlane.e[142]",
        "polyPlane.e[121]",
        "polyPlane.e[100]",
        "polyPlane.e[79]",
        "polyPlane.e[58]",
        "polyPlane.e[37]",
        "polyPlane.e[19]",
        "polyPlane.e[1]",
        "polyPlane.e[0]",
        "polyPlane.e[2]",
        "polyPlane.e[4]",
        "polyPlane.e[6]",
        "polyPlane.e[8]",
        "polyPlane.e[26]",
        "polyPlane.e[44]",
        "polyPlane.e[46]",
        "polyPlane.e[28]",
        "polyPlane.e[10]",
        "polyPlane.e[9]",
        "polyPlane.e[11]",
        "polyPlane.e[13]",
        "polyPlane.e[15]",
        "polyPlane.e[17]",
        "polyPlane.e[35]",
        "polyPlane.e[56]",
        "polyPlane.e[77]",
        "polyPlane.e[98]",
        "polyPlane.e[119]",
        "polyPlane.e[140]",
        "polyPlane.e[161]",
        "polyPlane.e[182]",
        "polyPlane.e[203]",
    )


def test_curve_distribute_between_vertices_closed() -> None:
    """
    This tests `maya_zen_tools.loop.curve_distribute_vertices` by creating
    a closed curve from the corner vertices, and distributing border
    vertices along the curve.
    """
    create_scene()
    selected_vertices: tuple[str, ...] = (
        "polyPlane.vtx[118]",
        "polyPlane.vtx[108]",
        "polyPlane.vtx[0]",
        "polyPlane.vtx[4]",
        "polyPlane.vtx[24]",
        "polyPlane.vtx[26]",
        "polyPlane.vtx[5]",
        "polyPlane.vtx[9]",
    )
    intermediate_vertices: tuple[str, ...] = (
        "polyPlane.vtx[6]",
        "polyPlane.vtx[115]",
        "polyPlane.vtx[97]",
        "polyPlane.vtx[96]",
        "polyPlane.vtx[25]",
        "polyPlane.vtx[2]",
        "polyPlane.vtx[15]",
        "polyPlane.vtx[74]",
        "polyPlane.vtx[111]",
        "polyPlane.vtx[41]",
        "polyPlane.vtx[112]",
        "polyPlane.vtx[116]",
        "polyPlane.vtx[52]",
        "polyPlane.vtx[42]",
        "polyPlane.vtx[7]",
        "polyPlane.vtx[3]",
        "polyPlane.vtx[113]",
        "polyPlane.vtx[86]",
        "polyPlane.vtx[19]",
        "polyPlane.vtx[30]",
        "polyPlane.vtx[31]",
        "polyPlane.vtx[14]",
        "polyPlane.vtx[117]",
        "polyPlane.vtx[75]",
        "polyPlane.vtx[1]",
        "polyPlane.vtx[114]",
        "polyPlane.vtx[10]",
        "polyPlane.vtx[109]",
        "polyPlane.vtx[110]",
        "polyPlane.vtx[64]",
        "polyPlane.vtx[63]",
        "polyPlane.vtx[20]",
        "polyPlane.vtx[107]",
        "polyPlane.vtx[85]",
        "polyPlane.vtx[8]",
        "polyPlane.vtx[53]",
    )
    cmds.select(clear=True)
    point_positions: tuple[tuple[float, float, float], ...] = tuple(
        cmds.pointPosition(vertex) for vertex in intermediate_vertices
    )
    vertex: str
    for vertex in selected_vertices:
        cmds.select(vertex, add=True)
    curve_distribute_vertices(
        use_selection_order=True,
        distribution_type=DistributionType.UNIFORM,
        close=True,
    )
    # Verify that intermediate vertices have moved
    index: int
    for index, vertex in enumerate(intermediate_vertices):
        assert cmds.pointPosition(vertex) != point_positions[index]


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
