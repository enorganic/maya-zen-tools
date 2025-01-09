from __future__ import annotations

import contextlib
from functools import partial
from itertools import chain
from typing import Callable, Iterable

from maya import cmds  # type: ignore

from maya_zen_tools import options
from maya_zen_tools._create import create_edges_rebuild_curve
from maya_zen_tools._traverse import (
    get_component_id,
    get_components_shape,
    iter_aligned_contiguous_edges,
    iter_edges_vertices,
    iter_selected_components,
    iter_vertices_path_proportional_positions,
    iter_vertices_path_uniform_positions,
)
from maya_zen_tools._ui import WINDOW
from maya_zen_tools.menu import LOFT_DISTRIBUTE_VERTICES_BETWEEN_EDGES_LABEL


def _surface_distribute_vertices_between_edges(
    surface_attribute: str,
    edge_loops: tuple[tuple[str, ...], ...],
    distribution_type: str = options.DistributionType.UNIFORM,
) -> set[str]:
    """
    Given a rebuildSurface node and one or more edge loops, distribute all
    vertices between the edge loops along the surface, and return the
    vertices as a set.
    """
    edges_ring: tuple[tuple[str, ...], ...] = tuple(
        _iter_edges_ring(edge_loops)
    )
    vertex_rings: tuple[tuple[str, ...], ...] = tuple(
        zip(*map(tuple, map(iter_edges_vertices, edges_ring)))
    )
    point_on_surface_info: str = cmds.createNode("pointOnSurfaceInfo")
    cmds.connectAttr(
        surface_attribute,
        f"{point_on_surface_info}.inputSurface",
    )
    progress_window: str = cmds.progressWindow(
        maxValue=len(vertex_rings),
    )
    v_position: float
    position: tuple[float, float, float]
    spans: int = len(edge_loops) - 1
    vertices_positions: dict[str, tuple[float, float, float]] = {}
    for v_position, vertex_ring in enumerate(vertex_rings):
        cmds.setAttr(f"{point_on_surface_info}.parameterV", v_position)
        u_position: float
        vertex: str
        for vertex, u_position in (
            iter_vertices_path_proportional_positions(vertex_ring, spans=spans)
            if distribution_type == options.DistributionType.PROPORTIONAL
            else iter_vertices_path_uniform_positions(vertex_ring, spans=spans)
        ):
            cmds.setAttr(f"{point_on_surface_info}.parameterU", u_position)
            position = cmds.getAttr(f"{point_on_surface_info}.position")[0]
            # The positions are stored for subsequent moving rather than
            # moved here in order to avoid having changes to the mesh
            # affect changes to the surface in cases where the surface
            # being used is created from polymesh edge curves
            vertices_positions[vertex] = position
        cmds.progressWindow(progress_window, progress=v_position)
    cmds.progressWindow(progress_window, endProgress=True)
    for vertex, position in vertices_positions.items():
        cmds.move(*position, vertex, absolute=True, worldSpace=True)
    return set(vertices_positions.keys())


def _iter_edges_ring(
    selected_edge_loops: tuple[tuple[str, ...], ...],
) -> Iterable[tuple[str, ...]]:
    """
    Given two or more sorted and directionally aligned edge loops,
    yield a ring of edge loops including those sandwiched between, in order.
    """
    shape: str = get_components_shape(chain(*selected_edge_loops))
    edge_rings: list[list[str]] = []
    selected_edge_ring: tuple[str, ...]
    for selected_edge_ring in zip(*selected_edge_loops):
        previous_edge_id: int = get_component_id(selected_edge_ring[0])
        edge: str
        edge_ring: list[str] = [selected_edge_ring[0]]
        for edge in selected_edge_ring[1:]:
            edge_id: int = get_component_id(edge)
            segment_edge_id: int
            segment_edge_ids: tuple[int, ...] = tuple(
                cmds.polySelect(
                    shape, query=True, edgeRingPath=(previous_edge_id, edge_id)
                )
            )
            if previous_edge_id != segment_edge_ids[0]:
                segment_edge_ids = tuple(reversed(segment_edge_ids))
            for segment_edge_id in segment_edge_ids[1:]:
                edge_ring.append(  # noqa: PERF401
                    f"{shape}.e[{segment_edge_id}]"
                )
            previous_edge_id = edge_id
        edge_rings.append(edge_ring)
    return zip(*edge_rings)


def loft_distribute_vertices_between_edges(
    *selected_edges: str,
    distribution_type: str = options.DistributionType.UNIFORM,
    create_deformer: bool = False,
) -> tuple[tuple[str, ...]] | tuple[tuple[str, ...], str, str, str]:
    """
    Given a selection of edge loop segments, aligned parallel to one
    another on a polygon mesh, distribute the vertices sandwiched between
    along a loft.
    """
    selected_edges = selected_edges or tuple(iter_selected_components("e"))
    selected_edge_loops: tuple[tuple[str, ...], ...] = tuple(
        iter_aligned_contiguous_edges(*selected_edges)
    )
    cmds.waitCursor(state=True)
    index: int
    edge_loop: tuple[str, ...]
    loft: str = cmds.createNode("loft", name="loftBetweenEdges#")
    for index, edge_loop in enumerate(selected_edge_loops):
        rebuild_curve: str = create_edges_rebuild_curve(edge_loop)
        cmds.connectAttr(
            f"{rebuild_curve}.outputCurve", f"{loft}.inputCurve[{index}]"
        )
    rebuild_surface: str = cmds.createNode(
        "rebuildSurface", name="loftBetweenEdgesRebuildSurface#"
    )
    cmds.connectAttr(
        f"{loft}.outputSurface",
        f"{rebuild_surface}.inputSurface",
    )
    cmds.setAttr(f"{rebuild_surface}.spansU", len(selected_edge_loops) - 1)
    cmds.setAttr(f"{rebuild_surface}.spansV", len(selected_edge_loops[0]))
    cmds.setAttr(f"{rebuild_surface}.keepRange", 2)
    cmds.setAttr(f"{rebuild_surface}.endKnots", 1)
    cmds.setAttr(f"{rebuild_surface}.direction", 0)
    vertices: set[str] = _surface_distribute_vertices_between_edges(
        f"{rebuild_surface}.outputSurface",
        edge_loops=selected_edge_loops,
        distribution_type=distribution_type,
    )
    faces: tuple[str, ...] = tuple(
        cmds.ls(
            *cmds.polyListComponentConversion(
                *vertices, fromVertex=True, toFace=True, internal=True
            ),
            flatten=True,
        )
    )
    if create_deformer:
        surface_transform: str = cmds.createNode(
            "transform", name="loftBetweenEdgesSurface#"
        )
        surface_shape: str = cmds.createNode(
            "nurbsSurface",
            name=f"{surface_transform}Shape",
            parent=surface_transform,
        )
        cmds.connectAttr(
            f"{loft}.outputSurface",
            f"{surface_shape}.create",
        )
        cmds.connectAttr(
            f"{rebuild_surface}.outputSurface",
            f"{surface_shape}.create",
            force=True,
        )
        cmds.delete(surface_shape, constructionHistory=True)
        wrap: str = cmds.proximityWrap(
            vertices,
        )
        cmds.proximityWrap(wrap, edit=True, addDrivers=[surface_shape])
        cmds.waitCursor(state=False)
        return (faces, surface_shape, surface_transform, wrap)
    cmds.delete(rebuild_surface)
    cmds.waitCursor(state=False)
    cmds.select(*faces)
    return (faces,)


def show_loft_distribute_vertices_between_edges_options() -> None:
    """
    Show a window with options to use when executing
    `loft_distribute_vertices_between_edges`.
    """
    # Get saved options
    get_option: Callable[[str], str | int | float | None] = partial(
        options.get_tool_option, "loft_distribute_vertices_between_edges"
    )
    # Create the window
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    cmds.window(
        WINDOW,
        width=240,
        height=100,
        title=(
            f"ZenTools: {LOFT_DISTRIBUTE_VERTICES_BETWEEN_EDGES_LABEL} Options"
        ),
    )
    column_layout: str = cmds.columnLayout(
        adjustableColumn=True, parent=WINDOW, columnAlign="left", margins=15
    )
    selected: int = 1
    with contextlib.suppress(ValueError):
        selected = ("UNIFORM", "PROPORTIONAL").index(
            get_option(  # type: ignore
                "distribution_type", options.DistributionType.UNIFORM
            )
        ) + 1
    cmds.radioButtonGrp(
        label="Distribution Type:",
        parent=column_layout,
        numberOfRadioButtons=2,
        label1="Uniform",
        label2="Proportional",
        columnAlign=(1, "left"),
        changeCommand1=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'loft_distribute_vertices_between_edges', 'distribution_type', "
            "'UNIFORM')"
        ),
        changeCommand2=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'loft_distribute_vertices_between_edges', 'distribution_type', "
            "'PROPORTIONAL')"
        ),
        select=selected,
        height=30,
    )
    cmds.separator(parent=column_layout)
    cmds.checkBox(
        label="Create Deformer",
        parent=column_layout,
        value=get_option("create_deformer", False),  # type: ignore
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'loft_distribute_vertices_between_edges', 'create_deformer', "
            "True)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'loft_distribute_vertices_between_edges', 'create_deformer', "
            "False)"
        ),
        height=30,
    )
    cmds.button(
        label="Distribute",
        parent=column_layout,
        command=(
            "from maya_zen_tools import loft\n"
            "from maya import cmds\n"
            "loft.do_loft_distribute_vertices_between_edges()\n"
            f"cmds.deleteUI('{WINDOW}')"
        ),
    )
    cmds.showWindow(WINDOW)


def do_loft_distribute_vertices_between_edges() -> None:
    """
    Execute `loft_distribute_vertices_between_edges`, getting arguments from
    the UI or saved options.
    """
    kwargs: dict[str, float | bool | str] = options.get_tool_options(
        "loft_distribute_vertices_between_edges"
    )
    loft_distribute_vertices_between_edges(**kwargs)  # type: ignore
