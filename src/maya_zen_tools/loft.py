from __future__ import annotations

import contextlib
from functools import partial
from itertools import chain
from math import ceil
from typing import Callable, Iterable

from maya import cmds  # type: ignore

from maya_zen_tools import options
from maya_zen_tools._create import (
    create_edges_rebuild_curve,
    create_node,
    create_uvs_rebuild_curve,
)
from maya_zen_tools._transform import center_pivot
from maya_zen_tools._traverse import (
    get_component_id,
    get_components_shape,
    iter_aligned_contiguous_edges,
    iter_aligned_contiguous_uvs,
    iter_edges_vertices,
    iter_selected_components,
    iter_shortest_uvs_path,
    iter_uvs_path_proportional_positions,
    iter_uvs_path_uniform_positions,
    iter_vertices_path_proportional_positions,
    iter_vertices_path_uniform_positions,
)
from maya_zen_tools._ui import WINDOW, set_wait_cursor_state
from maya_zen_tools.errors import EdgesNotOnSameRingError
from maya_zen_tools.menu import (
    LOFT_DISTRIBUTE_UVS_BETWEEN_EDGES_OR_UVS_LABEL,
    LOFT_DISTRIBUTE_VERTICES_BETWEEN_EDGES_LABEL,
)


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
    point_on_surface_info: str = create_node("pointOnSurfaceInfo")
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


def _surface_distribute_uvs(
    surface_attribute: str,
    uv_loops: tuple[tuple[str, ...], ...],
    distribution_type: str = options.DistributionType.UNIFORM,
) -> set[str]:
    """
    Given a surface output attribute and one or more UV loops, distribute all
    UVs between the loops along the surface in UV space, and return the
    UVs as a set.
    """
    uv_rings: tuple[tuple[str, ...], ...] = tuple(
        map(
            tuple,
            map(
                iter_shortest_uvs_path,
                zip(*uv_loops),
            ),
        )
    )
    point_on_surface_info: str = create_node("pointOnSurfaceInfo")
    cmds.connectAttr(
        surface_attribute,
        f"{point_on_surface_info}.inputSurface",
    )
    progress_window: str = cmds.progressWindow(
        maxValue=len(uv_rings),
    )
    v_position: float
    position: tuple[float, float, float]
    spans: int = len(uv_loops) - 1
    uvs_positions: dict[str, tuple[float, float, float]] = {}
    for v_position, uv_ring in enumerate(uv_rings):
        cmds.setAttr(f"{point_on_surface_info}.parameterV", v_position)
        u_position: float
        uv: str
        for uv, u_position in (
            iter_uvs_path_proportional_positions(uv_ring, spans=spans)
            if distribution_type == options.DistributionType.PROPORTIONAL
            else iter_uvs_path_uniform_positions(uv_ring, spans=spans)
        ):
            cmds.setAttr(f"{point_on_surface_info}.parameterU", u_position)
            position = cmds.getAttr(f"{point_on_surface_info}.position")[0][:2]
            # The positions are stored for subsequent moving rather than
            # moved here in order to avoid having changes to the mesh
            # affect changes to the surface in cases where the surface
            # being used is created from polymesh edge curves
            uvs_positions[uv] = position
        cmds.progressWindow(progress_window, progress=v_position)
    cmds.progressWindow(progress_window, endProgress=True)
    for uv, position in uvs_positions.items():
        cmds.polyEditUV(
            uv, uValue=position[0], vValue=position[1], relative=False
        )
    return set(uvs_positions.keys())


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
                or ()
            )
            if not segment_edge_ids:
                raise EdgesNotOnSameRingError(
                    shape, (previous_edge_id, edge_id)
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


def _create_wrap_deformer(
    deform_surface_attribute: str,
    base_surface_attribute: str,
    vertices: Iterable[str],
) -> str:
    """
    Create a wire deformer to manipulate specified vertices.
    """
    vertices = tuple(vertices)
    wrap: str = cmds.proximityWrap(
        vertices,
    )[0]
    cmds.connectAttr(
        base_surface_attribute,
        f"{wrap}.drivers[0].driverBindGeometry",
        force=True,
    )
    cmds.connectAttr(
        deform_surface_attribute,
        f"{wrap}.drivers[0].driverGeometry",
        force=True,
    )
    return wrap


def loft_distribute_vertices_between_edges(
    *selected_edges: str,
    distribution_type: str = options.DistributionType.UNIFORM,
    create_deformer: bool = False,
) -> tuple[str, ...] | tuple[tuple[str, ...], str, str, str]:
    """
    Given a selection of edge loop segments, aligned parallel to one
    another on a polygon mesh, distribute the vertices sandwiched between
    along a loft.
    """
    cleanup_items: list[str] = []
    selected_edges = selected_edges or tuple(iter_selected_components("e"))
    selected_edge_loops: tuple[tuple[str, ...], ...] = tuple(
        iter_aligned_contiguous_edges(*selected_edges)
    )
    set_wait_cursor_state(True)
    try:
        index: int
        edge_loop: tuple[str, ...]
        curve_transforms: list[str] = []
        curve_shapes: list[str] = []
        loft: str = create_node("loft", name="loft#")
        for index, edge_loop in enumerate(selected_edge_loops):
            rebuild_curve: str = create_edges_rebuild_curve(edge_loop)
            if create_deformer:
                curve_transform: str = create_node(
                    "transform", name="loftCurve#", skip_select=True
                )
                curve_shape: str = create_node(
                    "nurbsCurve",
                    name="loftCurveShape#",
                    parent=curve_transform,
                    skip_select=True,
                )
                cmds.connectAttr(
                    f"{rebuild_curve}.outputCurve", f"{curve_shape}.create"
                )
                center_pivot(curve_transform)
                cmds.connectAttr(
                    f"{curve_shape}.worldSpace[0]",
                    f"{loft}.inputCurve[{index}]",
                )
                curve_transforms.append(curve_transform)
                curve_shapes.append(curve_shape)
            else:
                cmds.connectAttr(
                    f"{rebuild_curve}.outputCurve",
                    f"{loft}.inputCurve[{index}]",
                )
            cleanup_items.append(rebuild_curve)
        rebuild_surface: str = create_node(
            "rebuildSurface", name="loftBetweenEdgesRebuildSurface#"
        )
        cleanup_items.append(rebuild_surface)
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
            surface_transform: str = create_node(
                "transform", name="loftBetweenEdges#"
            )
            surface_shape: str = create_node(
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
            cmds.setAttr(f"{surface_shape}.intermediateObject", 1)
            cmds.parent(*curve_transforms, surface_transform)
            wrap: str = _create_wrap_deformer(
                f"{rebuild_surface}.outputSurface",
                f"{surface_shape}.local",
                vertices,
            )

            def cleanup() -> None:
                """
                Disconnect the curves from the mesh, and the rebuilt surface
                from the base, so that changes aren't negated by having a base
                transform in concert with the driver
                """
                cmds.delete(*curve_shapes, constructionHistory=True)
                cmds.disconnectAttr(
                    f"{rebuild_surface}.outputSurface",
                    f"{surface_shape}.create",
                )

            cmds.evalDeferred(cleanup)
            # Go into object selection mode, in order to manipulate locators
            cmds.selectMode(object=True)
            # Select the middle locator
            cmds.select(curve_transforms[ceil(len(curve_transforms) / 2) - 1])
            set_wait_cursor_state(False)
            return (faces, surface_shape, surface_transform, wrap)
        cmds.delete(*cleanup_items)
        cmds.select(*faces)
    finally:
        set_wait_cursor_state(False)
    return faces


def loft_distribute_uvs_between_edges_or_uvs(
    *selection: str,
    distribution_type: str = options.DistributionType.UNIFORM,
) -> tuple[str, ...]:
    """
    Given a selection of edge loop segments or uv loop segments, aligned
    parallel to one another on a polygon mesh, distribute the UVs sandwiched
    between along a loft.
    """
    cleanup: list[str] = []
    selection = selection or tuple(iter_selected_components("e", "map"))
    selected_uvs: set[str] = set(
        iter_selected_components("map", selection=selection)
    )
    selected_edges: set[str] = set(
        iter_selected_components("e", selection=selection)
    )
    if selected_edges:
        selected_uvs |= set(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    *selected_edges,
                    fromEdge=True,
                    toUV=True,
                ),
                flatten=True,
            )
        )
    selected_uv_loops: tuple[tuple[str, ...], ...] = tuple(
        iter_aligned_contiguous_uvs(*selected_uvs)
    )
    set_wait_cursor_state(True)
    try:
        index: int
        uv_loop: tuple[str, ...]
        loft: str = create_node("loft", name="loftBetweenUVs#")
        for index, uv_loop in enumerate(selected_uv_loops):
            rebuild_curve: str
            curve_shape: str
            curve_transform: str
            rebuild_curve, curve_shape, curve_transform = (
                create_uvs_rebuild_curve(uv_loop)
            )
            cleanup.extend((rebuild_curve, curve_shape, curve_transform))
            cmds.connectAttr(
                f"{rebuild_curve}.outputCurve", f"{loft}.inputCurve[{index}]"
            )
        rebuild_surface: str = create_node(
            "rebuildSurface", name="loftBetweenEdgesRebuildSurface#"
        )
        cleanup.append(rebuild_surface)
        cmds.connectAttr(
            f"{loft}.outputSurface",
            f"{rebuild_surface}.inputSurface",
        )
        cmds.setAttr(f"{rebuild_surface}.spansU", len(selected_uv_loops) - 1)
        cmds.setAttr(f"{rebuild_surface}.spansV", len(selected_uv_loops[0]))
        cmds.setAttr(f"{rebuild_surface}.keepRange", 2)
        cmds.setAttr(f"{rebuild_surface}.endKnots", 1)
        cmds.setAttr(f"{rebuild_surface}.direction", 0)
        uvs: set[str] = _surface_distribute_uvs(
            f"{rebuild_surface}.outputSurface",
            uv_loops=selected_uv_loops,
            distribution_type=distribution_type,
        )
        faces: tuple[str, ...] = tuple(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    *uvs, fromUV=True, toFace=True, internal=True
                ),
                flatten=True,
            )
        )
        cmds.delete(*cleanup)
        cmds.select(*faces)
    finally:
        set_wait_cursor_state(False)
    return faces


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
    if cmds.windowPref(WINDOW, exists=True):
        cmds.windowPref(WINDOW, remove=True)
    cmds.window(
        WINDOW,
        width=450,
        height=100,
        title=(
            f"ZenTools: {LOFT_DISTRIBUTE_VERTICES_BETWEEN_EDGES_LABEL} Options"
        ),
        resizeToFitChildren=True,
        sizeable=False,
    )
    column_layout: str = cmds.columnLayout(
        adjustableColumn=True,
        parent=WINDOW,
        columnAlign="left",
        columnOffset=("both", 10),
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
    cmds.text(
        label="",
        parent=column_layout,
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


def show_loft_distribute_uvs_between_edges_or_uvs_options() -> None:
    """
    Show a window with options to use when executing
    `loft_distribute_uvs_between_edges_or_uvs`.
    """
    # Get saved options
    get_option: Callable[[str], str | int | float | None] = partial(
        options.get_tool_option, "loft_distribute_uvs_between_edges_or_uvs"
    )
    # Create the window
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    if cmds.windowPref(WINDOW, exists=True):
        cmds.windowPref(WINDOW, remove=True)
    cmds.window(
        WINDOW,
        width=470,
        height=65,
        title=(
            "ZenTools: "
            f"{LOFT_DISTRIBUTE_UVS_BETWEEN_EDGES_OR_UVS_LABEL} Options"
        ),
        resizeToFitChildren=True,
        sizeable=False,
    )
    column_layout: str = cmds.columnLayout(
        adjustableColumn=True,
        parent=WINDOW,
        columnAlign="left",
        columnOffset=("both", 10),
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
            "'loft_distribute_uvs_between_edges_or_uvs', 'distribution_type', "
            "'UNIFORM')"
        ),
        changeCommand2=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'loft_distribute_uvs_between_edges_or_uvs', 'distribution_type', "
            "'PROPORTIONAL')"
        ),
        select=selected,
        height=30,
    )
    cmds.button(
        label="Distribute",
        parent=column_layout,
        command=(
            "from maya_zen_tools import loft\n"
            "from maya import cmds\n"
            "loft.do_loft_distribute_uvs_between_edges_or_uvs()\n"
            f"cmds.deleteUI('{WINDOW}')"
        ),
    )
    cmds.showWindow(WINDOW)


def do_loft_distribute_uvs_between_edges_or_uvs() -> None:
    """
    Retrieve options and execute `loft_distribute_uvs_between_edges_or_uvs`.
    """
    kwargs: dict[str, float | bool | str] = options.get_tool_options(
        "loft_distribute_uvs_between_edges_or_uvs"
    )
    loft_distribute_uvs_between_edges_or_uvs(**kwargs)  # type: ignore
