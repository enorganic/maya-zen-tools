from __future__ import annotations

import contextlib
from functools import partial
from math import ceil
from operator import itemgetter
from typing import Callable, Iterable, Sequence

from maya import cmds  # type: ignore

from maya_zen_tools import options
from maya_zen_tools._create import (
    create_edges_rebuild_curve,
    create_locator,
    create_node,
    create_uv_edges_rebuild_curve,
)
from maya_zen_tools._traverse import (
    get_components_shape,
    iter_contiguous_edges,
    iter_contiguous_uv_edges,
    iter_selected_components,
    iter_shortest_uvs_path,
    iter_shortest_uvs_path_proportional_positions,
    iter_shortest_uvs_path_uniform_positions,
    iter_shortest_vertices_path,
    iter_shortest_vertices_path_proportional_positions,
    iter_shortest_vertices_path_uniform_positions,
    iter_sorted_uvs,
    iter_sorted_vertices,
    iter_uvs_edges,
    iter_vertices_edges,
)
from maya_zen_tools._ui import WINDOW, set_wait_cursor_state
from maya_zen_tools._utilities import as_tuple
from maya_zen_tools.menu import (
    CLOSE_CHECKBOX,
    CURVE_DISTRIBUTE_BETWEEN_UVS_LABEL,
    CURVE_DISTRIBUTE_BETWEEN_VERTICES_LABEL,
    SELECT_EDGES_BETWEEN_UVS_LABEL,
    SELECT_EDGES_BETWEEN_VERTICES_LABEL,
    SELECT_UVS_BETWEEN_UVS_LABEL,
)


def _get_vertices_locator_scale(vertices: Sequence[str]) -> float:
    """
    Get a locator scale appropriate for the given vertices.

    Parameters:
        vertices: A list of vertices.
    """
    bounding_box: tuple[float, float, float, float, float, float] = tuple(
        cmds.exactWorldBoundingBox(*vertices)
    )
    edges: tuple[str] = cmds.ls(
        *cmds.polyListComponentConversion(*vertices, toEdge=True), flatten=True
    )
    average_edge_length: float = sum(map(cmds.arclen, edges)) / len(edges)
    return max(
        average_edge_length / 3,
        max(
            abs(bounding_box[3] - bounding_box[0]),
            abs(bounding_box[4] - bounding_box[1]),
            abs(bounding_box[5] - bounding_box[2]),
        )
        / 10,
    )


def _create_curve_from_vertices(
    vertices: Sequence[str],
    *,
    create_locators: bool = False,
    close: bool = False,
) -> tuple[str, ...]:
    """
    Given a selection of vertices along a shared edge loop, create a curve
    passing between the vertices.

    The curve type will be an *arc* if 3 vertices are selected, otherwise the
    curve will emulate an "edit point" (EP) curve by creating a curve from
    a 0-width loft.

    Parameters:
        vertices: A list of vertices to create the curve from.
        create_locators: If `True`, create locators for manipulating the curve.
        close: If `True`, the curve will form a closed loop.
    """
    curve_transform: str = create_node(
        "transform", name="wire#", skip_select=True
    )
    curve_shape: str = create_node(
        "nurbsCurve",
        name=f"{curve_transform}Shape",
        parent=curve_transform,
        skip_select=True,
    )
    locator_scale: float = _get_vertices_locator_scale(vertices)
    index: int
    translation: tuple[float, float, float]
    locators: list[str] = []
    if len(vertices) == 3 and not close:  # noqa: PLR2004
        arc: str = create_node("makeThreePointCircularArc")
        for index, vertex in enumerate(vertices, 1):
            translation = cmds.xform(
                vertex, query=True, worldSpace=True, translation=True
            )
            if create_locators:
                locators.append(
                    create_locator(
                        translate=translation,
                        scale=locator_scale,
                        connect_translate=f"{arc}.point{index}",
                        parent=curve_transform,
                    )
                )
            else:
                cmds.setAttr(
                    f"{arc}.point{index}",
                    *translation,
                )
        cmds.connectAttr(f"{arc}.outputCurve", f"{curve_shape}.create")
    else:
        loft: str = create_node("loft")
        curve_from_surface_iso: str = create_node("curveFromSurfaceIso")
        cmds.setAttr(f"{curve_from_surface_iso}.isoparmDirection", 0)
        cmds.setAttr(f"{loft}.uniform", 0)
        if close:
            cmds.setAttr(f"{loft}.close", 1)
        for index, vertex in enumerate(vertices, 0):
            translation = cmds.xform(
                vertex, query=True, worldSpace=True, translation=True
            )
            point_matrix_mult: str = create_node("pointMatrixMult")
            if create_locators:
                locators.append(
                    create_locator(
                        translate=translation,
                        scale=locator_scale,
                        connect_translate=(f"{point_matrix_mult}.inPoint",),
                    )
                )
            else:
                cmds.setAttr(f"{point_matrix_mult}.inPoint", *translation)
            # Create a 0-length curve to use as an edit point in a loft
            # curve, parent that curve under our output curve transform
            # node, and delete the loft curve's original transform node
            loft_curve_transform: str = cmds.curve(
                objectSpace=True,
                degree=1,
                point=((0, 0, 0), (0, 0, 0)),
            )
            loft_curve_shape: str = cmds.listRelatives(
                loft_curve_transform, shapes=True, noIntermediate=True
            )[0]
            cmds.parent(
                loft_curve_shape, curve_transform, addObject=True, shape=True
            )
            cmds.delete(loft_curve_transform)
            # Connect the inverse matrix from our transform node to the
            # in-matrix of the point matrix multipliers
            cmds.connectAttr(
                f"{curve_transform}.worldInverseMatrix",
                f"{point_matrix_mult}.inMatrix",
            )
            # Connect the point matrix multiplier to the loft curve control
            # points
            cmds.connectAttr(
                f"{point_matrix_mult}.output",
                f"{loft_curve_shape}.controlPoints[0]",
            )
            cmds.connectAttr(
                f"{point_matrix_mult}.output",
                f"{loft_curve_shape}.controlPoints[1]",
            )
            # Connect the loft to the output curve shape
            cmds.connectAttr(
                f"{loft_curve_shape}.worldSpace[0]",
                f"{loft}.inputCurve[{index}]",
            )
        cmds.connectAttr(
            f"{loft}.outputSurface", f"{curve_from_surface_iso}.inputSurface"
        )
        cmds.connectAttr(
            f"{curve_from_surface_iso}.outputCurve", f"{curve_shape}.create"
        )
    return (curve_transform, curve_shape, *locators)


def _create_curve_from_uvs(
    uvs: Sequence[str],
    *,
    close: bool = False,
) -> tuple[str, ...]:
    """
    Given a selection of UVs along a shared edge loop, create a curve
    passing between the UVs.

    The curve type will be an *arc* if 3 UVs are selected, otherwise the
    curve will emulate an "edit point" (EP) curve by creating a curve from
    a 0-width loft.

    Parameters:
        uvs: A list of UVs to create the curve from.
        close: If `True`, the curve will form a closed loop.
    """
    transform: str = create_node(
        "transform", name="zenLoopCurve#", skip_select=True
    )
    shape: str = create_node(
        "nurbsCurve",
        name="zenLoopCurveShape#",
        parent=transform,
        skip_select=True,
    )
    index: int
    translation: tuple[float, float, float]
    if len(uvs) == 3 and not close:  # noqa: PLR2004
        arc: str = create_node("makeThreePointCircularArc")
        for index, uv in enumerate(uvs, 1):
            translation = (*cmds.polyEditUV(uv, query=True), 0)
            cmds.setAttr(
                f"{arc}.point{index}",
                *translation,
            )
        cmds.connectAttr(f"{arc}.outputCurve", f"{shape}.create")
    else:
        loft: str = create_node("loft")
        curve_from_surface_iso: str = create_node("curveFromSurfaceIso")
        cmds.setAttr(f"{curve_from_surface_iso}.isoparmDirection", 0)
        cmds.setAttr(f"{loft}.uniform", 0)
        if close:
            cmds.setAttr(f"{loft}.close", 1)
        for index, uv in enumerate(uvs, 0):
            translation = (*cmds.polyEditUV(uv, query=True), 0)
            point_matrix_mult: str = create_node("pointMatrixMult")
            cmds.setAttr(f"{point_matrix_mult}.inPoint", *translation)
            # Create a 0-length curve to use as an edit point in a loft
            # curve, parent that curve under our output curve transform
            # node, and delete the loft curve's original transform node
            loft_curve_transform: str = cmds.curve(
                objectSpace=True,
                degree=1,
                point=((0, 0, 0), (0, 0, 0)),
            )
            loft_curve_shape: str = cmds.listRelatives(
                loft_curve_transform, shapes=True, noIntermediate=True
            )[0]
            cmds.parent(
                loft_curve_shape, transform, addObject=True, shape=True
            )
            cmds.delete(loft_curve_transform)
            # Connect the inverse matrix from our transform node to the
            # in-matrix of the point matrix multipliers
            cmds.connectAttr(
                f"{transform}.worldInverseMatrix",
                f"{point_matrix_mult}.inMatrix",
            )
            # Connect the point matrix multiplier to the loft curve control
            # points
            cmds.connectAttr(
                f"{point_matrix_mult}.output",
                f"{loft_curve_shape}.controlPoints[0]",
            )
            cmds.connectAttr(
                f"{point_matrix_mult}.output",
                f"{loft_curve_shape}.controlPoints[1]",
            )
            # Connect the loft to the output curve shape
            cmds.connectAttr(
                f"{loft_curve_shape}.worldSpace[0]",
                f"{loft}.inputCurve[{index}]",
            )
        cmds.connectAttr(
            f"{loft}.outputSurface", f"{curve_from_surface_iso}.inputSurface"
        )
        cmds.connectAttr(
            f"{curve_from_surface_iso}.outputCurve", f"{shape}.create"
        )
    return (transform, shape)


def _create_wire_deformer(
    deform_curve_attribute: str,
    base_curve_attribute: str,
    vertices: Iterable[str],
) -> str:
    """
    Create a wire deformer to manipulate specified vertices.
    """
    vertices = tuple(vertices)
    wire: str = cmds.wire(
        vertices,
        # after=True,
        dropoffDistance=(0, float("inf")),
    )[0]
    cmds.connectAttr(base_curve_attribute, f"{wire}.baseWire[0]", force=True)
    cmds.connectAttr(
        deform_curve_attribute, f"{wire}.deformedWire[0]", force=True
    )
    return wire


def _distribute_vertices_loop_along_curve(
    selected_vertices: Sequence[str],
    curve_shape: str,
    curve_transform: str,
    *,
    distribution_type: str = options.DistributionType.UNIFORM,
    create_deformer: bool = False,
) -> tuple[str, tuple[str, ...]]:
    """
    Distribute vertices along a curve.

    Parameters:
        selected_vertices: Selected vertices. The distributed vertices
            will be the vertices forming an edge loop between the selected
            vertices.
        curve_shape: The curve shape node.
        distribution_type:
            UNIFORM: Distribute vertices equidistant along the curve.
            PROPORTIONAL: Distribute vertices such that edge lengths are
                proportional to their original lengths in relation the sum
                of all edge lengths.
        sampling: Curve sampling

    Returns:
        A tuple with two items:
        -   The curve shape name. If a deformer is created, this will not be
            the same as the the input curve shape.
        -   A tuple of the vertices distributed, in order
    """
    vertices_positions: tuple[tuple[str, float], ...] = tuple(
        iter_shortest_vertices_path_proportional_positions(selected_vertices)
        if distribution_type == options.DistributionType.PROPORTIONAL
        else iter_shortest_vertices_path_uniform_positions(selected_vertices)
    )
    # Rebuild the curve
    rebuild_curve: str = create_node("rebuildCurve")
    cmds.connectAttr(
        f"{curve_shape}.worldSpace[0]", f"{rebuild_curve}.inputCurve"
    )
    cmds.setAttr(f"{rebuild_curve}.rebuildType", 0)
    cmds.setAttr(f"{rebuild_curve}.spans", len(selected_vertices) - 1)
    cmds.setAttr(
        f"{rebuild_curve}.degree", cmds.getAttr(f"{curve_shape}.degree")
    )
    cmds.setAttr(f"{rebuild_curve}.keepTangents", 1)
    cmds.setAttr(f"{rebuild_curve}.keepEndPoints", 1)
    cmds.setAttr(f"{rebuild_curve}.keepRange", 2)
    # This point-on-curve info node will slide along the curve to get
    # transform values for the vertices
    point_on_curve_info: str = create_node("pointOnCurveInfo")
    point_matrix_mult: str = create_node("pointMatrixMult")
    cmds.connectAttr(
        f"{rebuild_curve}.outputCurve", f"{point_on_curve_info}.inputCurve"
    )
    cmds.connectAttr(
        f"{curve_shape}.worldMatrix[0]", f"{point_matrix_mult}.inMatrix"
    )
    cmds.connectAttr(
        f"{point_on_curve_info}.position", f"{point_matrix_mult}.inPoint"
    )
    vertex: str
    curve_position: float
    for vertex, curve_position in vertices_positions:
        cmds.setAttr(f"{point_on_curve_info}.parameter", curve_position)
        coordinates: tuple[str, str, str] = cmds.getAttr(
            f"{point_matrix_mult}.output"
        )[0]
        cmds.move(*coordinates, vertex, absolute=True, worldSpace=True)
    # Disconnect and delete temporary nodes
    cmds.disconnectAttr(
        f"{rebuild_curve}.outputCurve", f"{point_on_curve_info}.inputCurve"
    )
    cmds.delete(point_on_curve_info)
    cmds.delete(point_matrix_mult)
    if create_deformer:
        rebuilt_curve: str = create_node(
            "nurbsCurve",
            parent=curve_transform,
        )
        cmds.connectAttr(
            f"{rebuild_curve}.outputCurve", f"{rebuilt_curve}.create"
        )
        cmds.setAttr(f"{curve_shape}.intermediateObject", 1)
        cmds.setAttr(f"{rebuilt_curve}.intermediateObject", 0)
        # Use the rebuilt curve as a wire deformer
        _create_wire_deformer(
            f"{rebuild_curve}.outputCurve",
            f"{rebuilt_curve}.local",
            map(itemgetter(0), vertices_positions),
        )
        cmds.setAttr(f"{curve_shape}.intermediateObject", 0)
        cmds.setAttr(f"{rebuilt_curve}.intermediateObject", 1)
        cmds.setAttr(f"{curve_shape}.visibility", 0)
        # Disconnect the wire base from history, so that changes to the
        # wire aren't negated
        cmds.evalDeferred(
            lambda: cmds.disconnectAttr(
                f"{rebuild_curve}.outputCurve", f"{rebuilt_curve}.create"
            )
        )
        return rebuilt_curve, tuple(map(itemgetter(0), vertices_positions))
    cmds.delete(rebuild_curve)
    return curve_shape, tuple(map(itemgetter(0), vertices_positions))


def _distribute_uvs_loop_along_curve(
    selected_uvs: Sequence[str],
    curve_shape: str,
    *,
    distribution_type: str = options.DistributionType.UNIFORM,
) -> tuple[str, ...]:
    """
    Distribute UVs along a curve.

    Parameters:
        selected_uvs: Selected UVs. The distributed UVs
            will be the UVs forming an edge loop between the selected
            UVs.
        curve_shape: The curve shape node.
        distribution_type:
            UNIFORM: Distribute UVs equidistant along the curve.
            PROPORTIONAL: Distribute UVs such that edge lengths are
                proportional to their original lengths in relation the sum
                of all edge lengths.
        sampling: Curve sampling

    Returns:
        A tuple with two items:
        -   The curve shape name. If a deformer is created, this will not be
            the same as the the input curve shape.
        -   A tuple of the UVs distributed, in order
    """
    uvs_positions: tuple[tuple[str, float], ...] = tuple(
        iter_shortest_uvs_path_proportional_positions(selected_uvs)
        if distribution_type == options.DistributionType.PROPORTIONAL
        else iter_shortest_uvs_path_uniform_positions(selected_uvs)
    )
    # Rebuild the curve
    rebuild_curve: str = create_node("rebuildCurve")
    cmds.connectAttr(f"{curve_shape}.local", f"{rebuild_curve}.inputCurve")
    cmds.setAttr(f"{rebuild_curve}.rebuildType", 0)
    cmds.setAttr(f"{rebuild_curve}.spans", len(selected_uvs) - 1)
    cmds.setAttr(
        f"{rebuild_curve}.degree", cmds.getAttr(f"{curve_shape}.degree")
    )
    cmds.setAttr(f"{rebuild_curve}.keepTangents", 1)
    cmds.setAttr(f"{rebuild_curve}.keepEndPoints", 1)
    cmds.setAttr(f"{rebuild_curve}.keepRange", 2)
    # This point-on-curve info node will slide along the curve to get
    # transform values for the UVs
    point_on_curve_info: str = create_node("pointOnCurveInfo")
    point_matrix_mult: str = create_node("pointMatrixMult")
    cmds.connectAttr(
        f"{rebuild_curve}.outputCurve", f"{point_on_curve_info}.inputCurve"
    )
    cmds.connectAttr(
        f"{curve_shape}.worldMatrix[0]", f"{point_matrix_mult}.inMatrix"
    )
    cmds.connectAttr(
        f"{point_on_curve_info}.position", f"{point_matrix_mult}.inPoint"
    )
    uv: str
    curve_position: float
    for uv, curve_position in uvs_positions:
        cmds.setAttr(f"{point_on_curve_info}.parameter", curve_position)
        position: tuple[str, str, str] = cmds.getAttr(
            f"{point_matrix_mult}.output"
        )[0]
        cmds.polyEditUV(
            uv, uValue=position[0], vValue=position[1], relative=False
        )
    # Disconnect and delete temporary nodes
    cmds.disconnectAttr(
        f"{rebuild_curve}.outputCurve", f"{point_on_curve_info}.inputCurve"
    )
    cmds.delete(point_on_curve_info)
    cmds.delete(point_matrix_mult)
    cmds.delete(rebuild_curve)
    return tuple(map(itemgetter(0), uvs_positions))


def select_edges_between_vertices(
    *selected_vertices: str,
    use_selection_order: bool = False,
    close: bool = False,
) -> tuple[str, ...]:
    """
    Add the edges forming the shortest path between selected vertices to
    the current selection.

    Parameters:
        use_selection_order: If `True`, the edge path will follow the selection
            order, if two or more vertices are selected.
        close: If `True`, the vertices between the last and first selected
            vertex will be included.

    Returns:
        A tuple of the selected edges.
    """
    set_wait_cursor_state(True)
    try:
        if use_selection_order:
            # Check to make sure that selection order is being tracked, and
            # fall back to automatic sorting if not.
            use_selection_order = cmds.selectPref(
                trackSelectionOrder=True, query=True
            )
        if not use_selection_order:
            close = False
        # If vertices are not explicitly passed, we get them by
        # flattening the current selection of vertices
        selected_vertices = selected_vertices or tuple(
            iter_selected_components("vtx")
        )
        if not use_selection_order:
            # If we have opted not to use selection order, or are unable to
            # because it is not being tracked, we fall back to auomatic sorting
            selected_vertices = tuple(iter_sorted_vertices(selected_vertices))
        edges: tuple[str, ...] = tuple(
            iter_vertices_edges(
                iter_shortest_vertices_path(
                    (*selected_vertices, selected_vertices[0])
                    if close
                    else selected_vertices
                )
            )
        )
        # Select edges
        cmds.select(*edges, add=True)
        # Deselect vertices
        cmds.select(selected_vertices, deselect=True)
    finally:
        set_wait_cursor_state(False)
    return edges


def select_edges_between_uvs(
    *selected_uvs: str,
    use_selection_order: bool = False,
    close: bool = False,
) -> tuple[str, ...]:
    """
    Add the edges forming the shortest path between selected UVs to
    the current selection.

    Parameters:
        use_selection_order: If `True`, the edge path will follow the selection
            order, if two or more UVs are selected.
        close: If `True`, the UVs between the last and first selected
            UV will be included.

    Returns:
        A tuple of the selected edges.
    """
    set_wait_cursor_state(True)
    try:
        if use_selection_order:
            # Check to make sure that selection order is being tracked, and
            # fall back to automatic sorting if not.
            use_selection_order = cmds.selectPref(
                trackSelectionOrder=True, query=True
            )
        if not use_selection_order:
            close = False
        # If UVs are not explicitly passed, we get them by
        # flattening the current selection of UVs
        selected_uvs = selected_uvs or tuple(iter_selected_components("map"))
        if not use_selection_order:
            # If we have opted not to use selection order, or are unable to
            # because it is not being tracked, we fall back to auomatic sorting
            selected_uvs = tuple(iter_sorted_uvs(selected_uvs))
        edges: tuple[str, ...] = tuple(
            iter_uvs_edges(
                iter_shortest_uvs_path(
                    (*selected_uvs, selected_uvs[0]) if close else selected_uvs
                )
            )
        )
        # Select edges
        cmds.select(*edges, add=True)
        # Deselect UVs
        cmds.select(selected_uvs, deselect=True)
    finally:
        set_wait_cursor_state(False)
    return edges


def select_between_uvs(
    *selected_uvs: str,
    use_selection_order: bool = False,
    close: bool = False,
) -> tuple[str, ...]:
    """
    Add the UVs forming the shortest path between selected UVs to
    the current selection.

    Parameters:
        use_selection_order: If `True`, the path will follow the selection
            order, if two or more UVs are selected.
        close: If `True`, the UVs between the last and first selected
            UV will be included.

    Returns:
        A tuple of the selected UVs.
    """
    set_wait_cursor_state(True)
    try:
        if use_selection_order:
            # Check to make sure that selection order is being tracked, and
            # fall back to automatic sorting if not.
            use_selection_order = cmds.selectPref(
                trackSelectionOrder=True, query=True
            )
        if not use_selection_order:
            close = False
        # If UVs are not explicitly passed, we get them by
        # flattening the current selection of UVs
        selected_uvs = selected_uvs or tuple(iter_selected_components("map"))
        if not use_selection_order:
            # If we have opted not to use selection order, or are unable to
            # because it is not being tracked, we fall back to auomatic sorting
            selected_uvs = tuple(iter_sorted_uvs(selected_uvs))
        uvs: tuple[str, ...] = tuple(
            iter_shortest_uvs_path(
                (*selected_uvs, selected_uvs[0]) if close else selected_uvs
            )
        )
        # Select edges
        cmds.select(*uvs, add=True)
    finally:
        set_wait_cursor_state(False)
    return uvs


def curve_distribute_vertices(
    *selected_vertices: str,
    distribution_type: str = options.DistributionType.UNIFORM,
    create_deformer: bool = False,
    use_selection_order: bool = False,
    close: bool = False,
) -> tuple[str, ...]:
    """
    Create a curve passing between selected vertices and distribute all
    vertices on the edge loop segment along the curve.

    The curve type will be an *arc* if 3 vertices are selected, otherwise it
    will be an "edit point" (EP) curve.

    Parameters:
        selected_vertices: A list of vertices to create the curve from. If not
            provided, the current selection will be used.
        distribution_type: How to distribute vertices along the curve.
            UNIFORM: Distribute vertices equidistant along the curve.
            PROPORTIONAL: Distribute vertices such that edge lengths are
                proportional to their original lengths in relation the sum
                of all edge lengths.
        create_deformer: If `True`, create a deformer.
        use_selection_order: If `True`, the curve will be created in selection
            order, otherwise, it will be automatically sorted.
        close: If `True`, the curve distribution will form a closed loop, with
            the first selected vertex also being the last.

    Returns:
        A tuple of the affected edges (the same as the end state selection if
        `create_deformer == False`).
    """
    set_wait_cursor_state(True)
    try:
        if use_selection_order:
            # Check to make sure that selection order is being tracked, and
            # fall back to automatic sorting if not.
            use_selection_order = cmds.selectPref(
                trackSelectionOrder=True, query=True
            )
        if not use_selection_order:
            close = False
        # Store the original selection
        selection: list[str] = cmds.ls(orderedSelection=True, flatten=True)
        # If vertices are not explicitly passed, we get them by
        # flattening the current selection of vertices
        selected_vertices = selected_vertices or tuple(
            iter_selected_components("vtx")
        )
        # Raise an error if selected vertices span more than one mesh
        get_components_shape(selected_vertices)
        if not use_selection_order:
            # If we have opted not to use selection order, or are unable to
            # because it is not being tracked, we fall back to auomatic sorting
            selected_vertices = tuple(iter_sorted_vertices(selected_vertices))
        # Create the Curve
        curve_transform: str
        curve_shape: str
        locators: list[str]
        curve_transform, curve_shape, *locators = _create_curve_from_vertices(
            selected_vertices, create_locators=create_deformer, close=close
        )
        # Distribute Vertices Along the Curve
        vertices: tuple[str, ...]
        curve_shape, vertices = _distribute_vertices_loop_along_curve(
            (
                (*selected_vertices, selected_vertices[0])
                if close
                else selected_vertices
            ),
            curve_shape,
            curve_transform,
            distribution_type=distribution_type,
            create_deformer=create_deformer,
        )
        edges: tuple[str, ...] = tuple(iter_vertices_edges(vertices))
        if not create_deformer:
            # Cleanup the curve and history if not needed for creating a
            # deformer
            cmds.delete(curve_shape, constructionHistory=True)
            cmds.delete(curve_transform, constructionHistory=True)
            cmds.delete(curve_transform)
            cmds.select(*selection)
            cmds.select(*edges, add=True)
            cmds.select(selected_vertices, deselect=True)
            set_wait_cursor_state(False)
            return edges
        # Go into object selection mode, in order to manipulate locators
        cmds.selectMode(object=True)
        # Select a center locator, if there are more than two, otherwise select
        # an end locator
        cmds.select(locators[ceil(len(locators) / 2) - 1])
    finally:
        set_wait_cursor_state(False)
    return edges


def curve_distribute_uvs(
    *selected_uvs: str,
    distribution_type: str = options.DistributionType.UNIFORM,
    use_selection_order: bool = False,
    close: bool = False,
) -> tuple[str, ...]:
    """
    Create a curve passing between selected UVs and distribute all
    UVs on the edge loop segment along the curve.

    The curve type will be an *arc* if 3 UVs are selected, otherwise it
    will be an "edit point" (EP) curve.

    Parameters:
        selected_uvs: A list of UVs to create the curve from. If not
            provided, the current selection will be used.
        distribution_type: How to distribute UVs along the curve.
            UNIFORM: Distribute UVs equidistant along the curve.
            PROPORTIONAL: Distribute UVs such that edge lengths are
                proportional to their original lengths in relation the sum
                of all edge lengths.
        use_selection_order: If `True`, the curve will be created in selection
            order, otherwise, it will be automatically sorted.
        close: If `True`, the curve distribution will form a closed loop, with
            the first selected vertex also being the last.

    Returns:
        A tuple of the affected UVs.
    """
    set_wait_cursor_state(True)
    try:
        if use_selection_order:
            # Check to make sure that selection order is being tracked, and
            # fall back to automatic sorting if not.
            use_selection_order = cmds.selectPref(
                trackSelectionOrder=True, query=True
            )
        if not use_selection_order:
            close = False
        # Store the original selection
        selection: list[str] = cmds.ls(orderedSelection=True, flatten=True)
        # If UVs are not explicitly passed, we get them by
        # flattening the current selection of UVs
        selected_uvs = selected_uvs or tuple(iter_selected_components("map"))
        # Raise an error if selected UVs span more than one mesh
        get_components_shape(selected_uvs)
        if not use_selection_order:
            # If we have opted not to use selection order, or are unable to
            # because it is not being tracked, we fall back to auomatic sorting
            selected_uvs = tuple(iter_sorted_uvs(selected_uvs))
        # Create the Curve
        curve_transform: str
        curve_shape: str
        curve_transform, curve_shape = _create_curve_from_uvs(
            selected_uvs, close=close
        )
        # Distribute UVs Along the Curve
        uvs: tuple[str, ...] = _distribute_uvs_loop_along_curve(
            ((*selected_uvs, selected_uvs[0]) if close else selected_uvs),
            curve_shape,
            distribution_type=distribution_type,
        )
        edges: tuple[str, ...] = tuple(iter_uvs_edges(uvs))
        # Cleanup the curve and history
        cmds.delete(curve_shape, constructionHistory=True)
        cmds.delete(curve_transform, constructionHistory=True)
        cmds.delete(curve_transform)
        cmds.select(*selection, *uvs, add=True)
    finally:
        set_wait_cursor_state(False)
    return edges


@as_tuple
def create_curve_from_edges(*selected_edges: str) -> Iterable[str]:
    edges: tuple[str, ...]
    selected_edges = selected_edges or tuple(iter_selected_components("e"))
    for edges in iter_contiguous_edges(*selected_edges):
        rebuild_curve: str = create_edges_rebuild_curve(edges)
        curve_transform: str = create_node("transform", name="curveFromEdges#")
        curve_shape: str = create_node(
            "nurbsCurve",
            parent=curve_transform,
            name=f"{curve_transform}Shape",
        )
        cmds.connectAttr(
            f"{rebuild_curve}.outputCurve", f"{curve_shape}.create"
        )
        yield curve_shape


@as_tuple
def create_uv_curve_from_edges(*selected_edges: str) -> Iterable[str]:
    edges: tuple[str, ...]
    selected_edges = selected_edges or tuple(iter_selected_components("e"))
    for edges in iter_contiguous_uv_edges(*selected_edges):
        curve_shape: str = create_uv_edges_rebuild_curve(edges)[1]
        yield curve_shape


def show_curve_distribute_vertices_options() -> None:
    """
    Show a window with options to use when executing
    `curve_distribute_vertices`.
    """
    # Get saved options
    get_option: Callable[[str], str | int | float | None] = partial(
        options.get_tool_option, "curve_distribute_vertices"
    )
    # Create the window
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    if cmds.windowPref(WINDOW, exists=True):
        cmds.windowPref(WINDOW, remove=True)
    cmds.window(
        WINDOW,
        width=425,
        height=165,
        title=f"ZenTools: {CURVE_DISTRIBUTE_BETWEEN_VERTICES_LABEL} Options",
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
            "'curve_distribute_vertices', 'distribution_type', "
            "'UNIFORM')"
        ),
        changeCommand2=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_vertices', 'distribution_type', "
            "'PROPORTIONAL')"
        ),
        select=selected,
        height=30,
    )
    cmds.separator(parent=column_layout)
    use_selection_order: bool = get_option(  # type: ignore
        "use_selection_order", False
    )
    cmds.checkBox(
        label="Use Selection Order",
        parent=column_layout,
        value=use_selection_order,  # type: ignore
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_vertices', 'use_selection_order', "
            "True)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=False)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_vertices', 'use_selection_order', "
            "False)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=True)"
        ),
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
            "'curve_distribute_vertices', 'create_deformer', "
            "True)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_vertices', 'create_deformer', "
            "False)"
        ),
        height=30,
    )
    cmds.separator(parent=column_layout)
    cmds.checkBox(
        CLOSE_CHECKBOX,
        label="Close",
        parent=column_layout,
        value=get_option("close", False),  # type: ignore
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_vertices', 'close', "
            "True)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_vertices', 'close', "
            "False)"
        ),
        height=30,
    )
    if not use_selection_order:
        cmds.disable(CLOSE_CHECKBOX, value=True)
    cmds.button(
        label="Distribute",
        parent=column_layout,
        command=(
            "from maya_zen_tools import loop\n"
            "from maya import cmds\n"
            "loop.do_curve_distribute_vertices()\n"
            f"cmds.deleteUI('{WINDOW}')"
        ),
    )
    cmds.text(
        label="",
        parent=column_layout,
    )
    cmds.showWindow(WINDOW)


def do_curve_distribute_vertices() -> None:
    """
    Execute `curve_distribute_vertices`, getting arguments from the UI or
    saved options.
    """
    kwargs: dict[str, float | bool | str] = options.get_tool_options(
        "curve_distribute_vertices"
    )
    curve_distribute_vertices(**kwargs)  # type: ignore


def show_curve_distribute_uvs_options() -> None:
    """
    Show a window with options to use when executing
    `curve_distribute_uvs`.
    """
    # Get saved options
    get_option: Callable[[str], str | int | float | None] = partial(
        options.get_tool_option, "curve_distribute_uvs"
    )
    # Create the window
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    if cmds.windowPref(WINDOW, exists=True):
        cmds.windowPref(WINDOW, remove=True)
    cmds.window(
        WINDOW,
        width=390,
        height=130,
        title=f"ZenTools: {CURVE_DISTRIBUTE_BETWEEN_UVS_LABEL} Options",
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
            "'curve_distribute_uvs', 'distribution_type', "
            "'UNIFORM')"
        ),
        changeCommand2=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_uvs', 'distribution_type', "
            "'PROPORTIONAL')"
        ),
        select=selected,
        height=30,
    )
    cmds.separator(parent=column_layout)
    use_selection_order: bool = get_option(  # type: ignore
        "use_selection_order", False
    )
    cmds.checkBox(
        label="Use Selection Order",
        parent=column_layout,
        value=use_selection_order,  # type: ignore
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_uvs', 'use_selection_order', "
            "True)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=False)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_uvs', 'use_selection_order', "
            "False)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=True)"
        ),
        height=30,
    )
    cmds.separator(parent=column_layout)
    cmds.checkBox(
        CLOSE_CHECKBOX,
        label="Close",
        parent=column_layout,
        value=get_option("close", False),  # type: ignore
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_uvs', 'close', "
            "True)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'curve_distribute_uvs', 'close', "
            "False)"
        ),
        height=30,
    )
    if not use_selection_order:
        cmds.disable(CLOSE_CHECKBOX, value=True)
    cmds.button(
        label="Distribute",
        parent=column_layout,
        command=(
            "from maya_zen_tools import loop\n"
            "from maya import cmds\n"
            "loop.do_curve_distribute_uvs()\n"
            f"cmds.deleteUI('{WINDOW}')"
        ),
    )
    cmds.text(
        label="",
        parent=column_layout,
    )
    cmds.showWindow(WINDOW)


def do_curve_distribute_uvs() -> None:
    """
    Execute `curve_distribute_uvs`, getting arguments from the UI or
    saved options.
    """
    kwargs: dict[str, float | bool | str] = options.get_tool_options(
        "curve_distribute_uvs"
    )
    curve_distribute_uvs(**kwargs)  # type: ignore


def show_select_edges_between_vertices_options() -> None:
    """
    Show a window with options to use when executing
    `select_edges_between_vertices`.
    """
    # Get saved options
    get_option: Callable[[str], str | int | float | None] = partial(
        options.get_tool_option, "select_edges_between_vertices"
    )
    # Create the window
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    if cmds.windowPref(WINDOW, exists=True):
        cmds.windowPref(WINDOW, remove=True)
    cmds.window(
        WINDOW,
        width=400,
        height=100,
        title=f"ZenTools: {SELECT_EDGES_BETWEEN_VERTICES_LABEL} Options",
        resizeToFitChildren=True,
        sizeable=False,
    )
    column_layout: str = cmds.columnLayout(
        adjustableColumn=True,
        parent=WINDOW,
        columnAlign="left",
        columnOffset=("both", 10),
    )
    use_selection_order: bool = get_option(  # type: ignore
        "use_selection_order", False
    )
    cmds.checkBox(
        label="Use Selection Order",
        parent=column_layout,
        value=use_selection_order,
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_edges_between_vertices', 'use_selection_order', "
            "True)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=False)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_edges_between_vertices', 'use_selection_order', "
            "False)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=True)"
        ),
        height=30,
    )
    cmds.separator(parent=column_layout)
    cmds.checkBox(
        CLOSE_CHECKBOX,
        label="Close",
        parent=column_layout,
        value=get_option("close", False),  # type: ignore
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_edges_between_vertices', 'close', "
            "True)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_edges_between_vertices', 'close', "
            "False)"
        ),
        height=30,
    )
    if not use_selection_order:
        cmds.disable(CLOSE_CHECKBOX, value=True)
    cmds.button(
        label="Select",
        parent=column_layout,
        command=(
            "from maya_zen_tools import loop\n"
            "from maya import cmds\n"
            "loop.do_select_edges_between_vertices()\n"
            f"cmds.deleteUI('{WINDOW}')"
        ),
    )
    cmds.text(
        label="",
        parent=column_layout,
    )
    cmds.showWindow(WINDOW)


def do_select_edges_between_vertices() -> None:
    """
    Execute `curve_distribute_vertices`, getting arguments from the UI or
    saved options.
    """
    kwargs: dict[str, float | bool | str] = options.get_tool_options(
        "select_edges_between_vertices"
    )
    select_edges_between_vertices(**kwargs)  # type: ignore


def show_select_edges_between_uvs_options() -> None:
    """
    Show a window with options to use when executing
    `select_edges_between_uvs`.
    """
    # Get saved options
    get_option: Callable[[str], str | int | float | None] = partial(
        options.get_tool_option, "select_edges_between_uvs"
    )
    # Create the window
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    if cmds.windowPref(WINDOW, exists=True):
        cmds.windowPref(WINDOW, remove=True)
    cmds.window(
        WINDOW,
        width=400,
        height=100,
        title=f"ZenTools: {SELECT_EDGES_BETWEEN_UVS_LABEL} Options",
        resizeToFitChildren=True,
        sizeable=False,
    )
    column_layout: str = cmds.columnLayout(
        adjustableColumn=True,
        parent=WINDOW,
        columnAlign="left",
        columnOffset=("both", 10),
    )
    use_selection_order: bool = get_option(  # type: ignore
        "use_selection_order", False
    )
    cmds.checkBox(
        label="Use Selection Order",
        parent=column_layout,
        value=use_selection_order,
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_edges_between_uvs', 'use_selection_order', "
            "True)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=False)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_edges_between_uvs', 'use_selection_order', "
            "False)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=True)"
        ),
        height=30,
    )
    cmds.separator(parent=column_layout)
    cmds.checkBox(
        CLOSE_CHECKBOX,
        label="Close",
        parent=column_layout,
        value=get_option("close", False),  # type: ignore
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_edges_between_uvs', 'close', "
            "True)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_edges_between_uvs', 'close', "
            "False)"
        ),
        height=30,
    )
    if not use_selection_order:
        cmds.disable(CLOSE_CHECKBOX, value=True)
    cmds.button(
        label="Select",
        parent=column_layout,
        command=(
            "from maya_zen_tools import loop\n"
            "from maya import cmds\n"
            "loop.do_select_edges_between_uvs()\n"
            f"cmds.deleteUI('{WINDOW}')"
        ),
    )
    cmds.showWindow(WINDOW)


def do_select_edges_between_uvs() -> None:
    """
    Execute `curve_distribute_uvs`, getting arguments from the UI or
    saved options.
    """
    kwargs: dict[str, float | bool | str] = options.get_tool_options(
        "select_edges_between_uvs"
    )
    select_edges_between_uvs(**kwargs)  # type: ignore


def show_select_between_uvs_options() -> None:
    """
    Show a window with options to use when executing
    `select_between_uvs`.
    """
    # Get saved options
    get_option: Callable[[str], str | int | float | None] = partial(
        options.get_tool_option, "select_between_uvs"
    )
    # Create the window
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    cmds.window(
        WINDOW,
        width=380,
        height=100,
        title=f"ZenTools: {SELECT_UVS_BETWEEN_UVS_LABEL} Options",
        resizeToFitChildren=True,
        sizeable=False,
    )
    column_layout: str = cmds.columnLayout(
        adjustableColumn=True,
        parent=WINDOW,
        columnAlign="left",
        columnOffset=("both", 10),
    )
    use_selection_order: bool = get_option(  # type: ignore
        "use_selection_order", False
    )
    cmds.checkBox(
        label="Use Selection Order",
        parent=column_layout,
        value=use_selection_order,
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_between_uvs', 'use_selection_order', "
            "True)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=False)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_between_uvs', 'use_selection_order', "
            "False)\n"
            "from maya import cmds\n"
            f"cmds.disable('{CLOSE_CHECKBOX}', value=True)"
        ),
        height=30,
    )
    cmds.separator(parent=column_layout)
    cmds.checkBox(
        CLOSE_CHECKBOX,
        label="Close",
        parent=column_layout,
        value=get_option("close", False),  # type: ignore
        onCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_between_uvs', 'close', "
            "True)"
        ),
        offCommand=(
            "from maya_zen_tools import options\n"
            "options.set_tool_option("
            "'select_between_uvs', 'close', "
            "False)"
        ),
        height=30,
    )
    if not use_selection_order:
        cmds.disable(CLOSE_CHECKBOX, value=True)
    cmds.button(
        label="Select",
        parent=column_layout,
        command=(
            "from maya_zen_tools import loop\n"
            "from maya import cmds\n"
            "loop.do_select_between_uvs()\n"
            f"cmds.deleteUI('{WINDOW}')"
        ),
    )
    cmds.text(
        label="",
        parent=column_layout,
    )
    cmds.showWindow(WINDOW)


def do_select_between_uvs() -> None:
    """
    Execute `curve_distribute_uvs`, getting arguments from the UI or
    saved options.
    """
    kwargs: dict[str, float | bool | str] = options.get_tool_options(
        "select_between_uvs"
    )
    select_between_uvs(**kwargs)  # type: ignore
