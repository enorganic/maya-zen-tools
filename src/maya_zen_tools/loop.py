from __future__ import annotations

import contextlib
from functools import partial
from itertools import islice
from math import ceil
from operator import itemgetter
from typing import Callable, Iterable, Sequence, cast
from warnings import warn

from maya import cmds  # type: ignore

from maya_zen_tools import options
from maya_zen_tools._utilities import (
    create_locator,
    get_components_shape,
    get_expanded_vertices,
    iter_sorted_edge_loop_vertices,
)
from maya_zen_tools.errors import (
    MultipleVertexPathsPossibleWarning,
    NonContiguousMeshSelectionError,
    TooManyShapesError,
)
from maya_zen_tools.menu import CURVE_DISTRIBUTE_BETWEEN_VERTICES_LABEL

WINDOW: str = "zenToolsWindow"
DISTRIBUTION_TYPE_RADIO_BUTTON: str = "zenToolsDistributeTypeRadioButton"


class DistributionType:
    """
    An enumeration of the different types of distribution that can be used
    when creating a loop.

    Attributes:
        UNIFORM: Distribute vertices equidistant along the curve.
        PROPORTIONAL: Distribute vertices such that edge lengths are
            proportional to their original lengths in relation the sum
            of all edge lengths.
    """

    UNIFORM: str = "UNIFORM"
    PROPORTIONAL: str = "PROPORTIONAL"


def _iter_shortest_vertex_path(
    start_vertex: str, end_vertex: str
) -> Iterable[str]:
    """
    Get the shortest vertex path by intersecting expanding rings of vertices.
    This produces a more predictable/consistent result than the polySelect
    command with the shortestEdgePath option.

    Parameters:
        start_vertex: The vertex at the start of the path.
        end_vertex: The vertex at the end of the path.
    """
    start_vertex_rings: list[set[str]] = [{start_vertex}]
    end_vertex_rings: list[set[str]] = [{end_vertex}]
    # Getting the component shape is primarily done
    # in order to raise an error if the vertices are not on the same shape,
    # but is also used when raising an error.
    shape: str = get_components_shape((start_vertex, end_vertex))
    vertices: set[str] = {start_vertex}
    expanded_vertices: set[str]
    ring_vertices: set[str]
    # Get a set of rings grown from the start vertex
    while end_vertex not in vertices:
        expanded_vertices = get_expanded_vertices(vertices)
        ring_vertices = expanded_vertices - vertices
        if not ring_vertices:
            # If we can't expand any further, and still haven't reached
            # the end vertex, it's not a contiguous mesh
            raise NonContiguousMeshSelectionError(shape)
        start_vertex_rings.append(ring_vertices)
        vertices = expanded_vertices
    vertices = {end_vertex}
    # Get a set of rings grown from the end vertex
    while start_vertex not in vertices:
        # Stop when we've reached the start vertex
        if start_vertex in vertices:
            break
        expanded_vertices = get_expanded_vertices(vertices)
        ring_vertices = expanded_vertices - vertices
        end_vertex_rings.append(ring_vertices)
        vertices = expanded_vertices
    # We should now have two sets of vertex rings of equal length
    start_vertex_ring: set[str]
    end_vertex_ring: set[str]
    vertex: str = ""
    for start_vertex_ring, end_vertex_ring in zip(
        start_vertex_rings, reversed(end_vertex_rings)
    ):
        ring_intersection: set[str] = start_vertex_ring & end_vertex_ring
        if len(ring_intersection) > 1:
            # There will typically be only one intersecting vertex, the
            # exception being for a mesh with interior holes coinciding with
            # our vertex path, in which case we need to narrow our traversal
            # to only select vertices on one side of the hole (which side is
            # selected at random, by necessity)
            if vertex:
                # Intersect with only the vertices adjacent to the previously
                # yielded vertex, to prevent hole-jumping
                ring_intersection &= get_expanded_vertices({vertex})
            warn(
                (
                    "Multiple vertex paths possible between "
                    f"{start_vertex} and {end_vertex}"
                ),
                category=MultipleVertexPathsPossibleWarning,
                stacklevel=2,
            )
        vertex = ring_intersection.pop()
        yield vertex


def _iter_shortest_vertices_path(vertices: Iterable[str]) -> Iterable[str]:
    """
    Given two vertices, yield the vertices forming the shortest
    path between them.

    Parameters:
        vertices: Two or more vertices.
    """
    vertices = iter(vertices)
    try:
        start_vertex: str = next(vertices)
    except StopIteration:
        return
    is_first: bool = True
    end_vertex: str
    for end_vertex in vertices:
        segment_vertices: Iterable[str] = _iter_shortest_vertex_path(
            start_vertex,
            end_vertex,
        )
        yield from (
            segment_vertices
            if is_first
            # Skip the first vertex for segments after the first
            else islice(segment_vertices, 1, None)
        )
        start_vertex = end_vertex
        is_first = False


def _iter_shortest_vertices_path_proportionate_positions(
    selected_vertices: Iterable[str],
) -> Iterable[tuple[str, float]]:
    """
    Given two or more vertices, yield the vertices forming the shortest
    path between them, along with a number from 0-1 indicating where on the
    path each vertex should be positioned for proportional distribution.

    Parameters:
        vertices: Two or more vertices.

    Yields:
        A tuple containing the vertex name and a number from 0-1 indicating
        where on the path the vertex should be positioned.
    """
    vertices: list[str] = []
    edge_lengths: list[float] = []
    previous_vertex: str = ""
    vertex: str
    edge_length: float
    for vertex in _iter_shortest_vertices_path(selected_vertices):
        vertices.append(vertex)
        if previous_vertex:
            edge: str = cmds.polyListComponentConversion(
                previous_vertex,
                vertex,
                fromVertex=True,
                toEdge=True,
                internal=True,
            )[0]
            edge_length = cmds.arclen(edge)
            if not edge_length:
                raise ValueError(edge)
            edge_lengths.append(
                # The length of the preceding edge
                edge_length
            )
        else:
            edge_lengths.append(0)
        previous_vertex = vertex
    total_edge_length: float = sum(edge_lengths)
    traversed_edge_length: float = 0.0
    for vertex, edge_length in zip(vertices, edge_lengths):
        traversed_edge_length += edge_length
        yield vertex, traversed_edge_length / total_edge_length


def _iter_shortest_vertices_path_uniform_positions(
    selected_vertices: Iterable[str],
) -> Iterable[tuple[str, float]]:
    """
    Given two or more vertices, yield the vertices forming the shortest
    path between them, along with a number from 0-1 indicating where on the
    path each vertex should be positioned for uniform distribution.

    Parameters:
        vertices: Two or more vertices.

    Yields:
        A tuple containing the vertex name and a number from 0-1 indicating
        where on the path the vertex should be positioned.
    """
    vertices: tuple[str, ...] = tuple(
        cast(
            Iterable[str],
            _iter_shortest_vertices_path(selected_vertices),
        )
    )
    length: int = len(vertices) - 1
    index: int
    for index, vertex in enumerate(
        vertices,
    ):
        yield vertex, index / length


def _get_vertices_locator_scale(vertices: Sequence[str]) -> float:
    """
    Get a locator scale appropriate for the given vertices.

    Parameters:
        vertices: A list of vertices.
    """
    edges: list[str] = cmds.ls(
        *cmds.polyListComponentConversion(*vertices, toEdge=True), flatten=True
    )
    average_edge_length: float = sum(map(cmds.arclen, edges)) / len(edges)
    return average_edge_length / 3


def _create_curve_from_vertices(
    vertices: Sequence[str], *, create_locators: bool = False
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
    """
    transform: str = cmds.createNode(
        "transform", name="zenLoopCurve#", skipSelect=True
    )
    shape: str = cmds.createNode(
        "nurbsCurve",
        name="zenLoopCurveShape#",
        parent=transform,
        skipSelect=True,
    )
    locator_scale: float = _get_vertices_locator_scale(vertices)
    index: int
    translation: tuple[float, float, float]
    locators: list[str] = []
    if len(vertices) == 3:  # noqa: PLR2004
        arc: str = cmds.createNode("makeThreePointCircularArc")
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
                    )
                )
            else:
                cmds.setAttr(
                    f"{arc}.point{index}",
                    *translation,
                )
        cmds.connectAttr(f"{arc}.outputCurve", f"{shape}.create")
    else:
        loft: str = cmds.createNode("loft")
        curve_from_surface_iso: str = cmds.createNode("curveFromSurfaceIso")
        cmds.setAttr(f"{curve_from_surface_iso}.isoparmDirection", 0)
        cmds.setAttr(f"{loft}.uniform", 0)
        for index, vertex in enumerate(vertices, 0):
            translation = cmds.xform(
                vertex, query=True, worldSpace=True, translation=True
            )
            point_matrix_mult: str = cmds.createNode("pointMatrixMult")
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
    return (transform, shape, *locators)


def _create_wire_deformer(
    deform_curve_attribute: str,
    base_curve_attribute: str,
    vertices: Iterable[str],
) -> str:
    """
    Create a wire deformer to manipulate specified vertices.
    """
    vertices = tuple(vertices)
    shape: str = get_components_shape(vertices)
    wire: str = cmds.wire(
        vertices,
        after=True,
        dropoffDistance=(0, float("inf")),
    )[0]
    cmds.connectAttr(base_curve_attribute, f"{wire}.baseWire[0]", force=True)
    cmds.connectAttr(
        deform_curve_attribute, f"{wire}.deformedWire[0]", force=True
    )
    new_shape: str = cmds.listConnections(
        f"{wire}.outputGeometry", source=False, destination=True, shapes=True
    )[0]
    # Rename the base shape and new shape such that the new shape inherits
    # the base shape's name
    cmds.rename(shape, f"{shape}WireBase")
    cmds.rename(new_shape, shape)
    return wire


def _distribute_vertices_loop_along_curve(
    selected_vertices: Sequence[str],
    curve_shape: str,
    curve_transform: str,
    *,
    distribution_type: str = DistributionType.UNIFORM,
    create_deformer: bool = False,
    sampling: int = 3,
) -> str:
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
        The curve shape name. If a deformer is created, this will not be
        the same as the the input curve shape.
    """
    vertices_positions: tuple[tuple[str, float], ...] = tuple(
        _iter_shortest_vertices_path_proportionate_positions(selected_vertices)
        if distribution_type == DistributionType.PROPORTIONAL
        else _iter_shortest_vertices_path_uniform_positions(selected_vertices)
    )
    # Rebuild the curve to have a 0 to 1 parameter range
    rebuild_curve: str = cmds.createNode("rebuildCurve")
    cmds.connectAttr(f"{curve_shape}.local", f"{rebuild_curve}.inputCurve")
    cmds.setAttr(f"{rebuild_curve}.rebuildType", 0)
    cmds.setAttr(
        f"{rebuild_curve}.spans", (len(vertices_positions)) * sampling
    )
    cmds.setAttr(
        f"{rebuild_curve}.degree", cmds.getAttr(f"{curve_shape}.degree")
    )
    cmds.setAttr(f"{rebuild_curve}.keepTangents", 1)
    cmds.setAttr(f"{rebuild_curve}.keepEndPoints", 1)
    cmds.setAttr(f"{rebuild_curve}.keepRange", 0)
    # This point-on-curve info node will slide along the curve to get
    # transform values for the vertices
    point_on_curve_info: str = cmds.createNode("pointOnCurveInfo")
    point_matrix_mult: str = cmds.createNode("pointMatrixMult")
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
        rebuilt_curve: str = cmds.createNode(
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
        cmds.evalDeferred(
            "cmds.disconnectAttr("
            f'"{rebuild_curve}.outputCurve", "{rebuilt_curve}.create"'
            ")"
        )
        return rebuilt_curve
    cmds.delete(rebuild_curve)
    return curve_shape


def curve_distribute_vertices(
    *,
    distribution_type: str = DistributionType.UNIFORM,
    create_deformer: bool = False,
) -> None:
    """
    Create a curve passing between selected vertices and distribute all
    vertices on the edge loop segment along the curve.

    The curve type will be an *arc* if 3 vertices are selected, otherwise it
    will be an "edit point" (EP) curve.

    Parameters:
        selection: A list of vertices to create the curve from. If not
            provided, the current selection will be used.
        distribution_type: How to distribute vertices along the curve.
            UNIFORM: Distribute vertices equidistant along the curve.
            PROPORTIONAL: Distribute vertices such that edge lengths are
                proportional to their original lengths in relation the sum
                of all edge lengths.
        create_deformer: If `True`, create a deformer.
    """
    cmds.waitCursor(state=True)
    # If selection order is being tracked, we can sort vertices by the order
    # in which they were selected, so we want to determine this first
    tracking_selection_order: bool = cmds.selectPref(
        trackSelectionOrder=True, query=True
    )
    selection: tuple[str] = tuple(cmds.ls(orderedSelection=True, flatten=True))
    selected_vertices: tuple[str, ...] = tuple(
        cmds.ls(
            *cmds.polyListComponentConversion(
                *selection, fromVertex=True, toVertex=True
            ),
            orderedSelection=True,
            flatten=True,
        )
    )
    # Get the list of polygon meshes that the selected vertices belong to
    shapes: tuple[str] = tuple(cmds.ls(*selected_vertices, objectsOnly=True))
    if len(shapes) != 1:
        raise TooManyShapesError(shapes)
    if not tracking_selection_order:
        # If selection order is not being tracked, we need to auto-sort
        # the vertices
        selected_vertices = tuple(
            iter_sorted_edge_loop_vertices(selected_vertices)
        )
    # Create the Curve
    curve_transform: str
    curve_shape: str
    locators: list[str]
    curve_transform, curve_shape, *locators = _create_curve_from_vertices(
        selected_vertices, create_locators=create_deformer
    )
    # Distribute Vertices Along the Curve
    curve_shape = _distribute_vertices_loop_along_curve(
        selected_vertices,
        curve_shape,
        curve_transform,
        distribution_type=distribution_type,
        create_deformer=create_deformer,
    )
    if not create_deformer:
        # Cleanup the curve and history if not needed for creating a deformer
        cmds.delete(curve_shape, constructionHistory=True)
        cmds.delete(curve_transform, constructionHistory=True)
        cmds.delete(curve_transform)
        cmds.select(selection)
        return
    # Go into object selection mode, in order to manipulate locators
    cmds.selectMode(object=True)
    # Select a center locator, if there are more than two, otherwise select
    # an end locator
    cmds.select(locators[ceil(len(locators) / 2)])
    cmds.waitCursor(state=False)


def show_curve_distribute_vertices_options() -> None:
    """
    Show a window with loop distribute options.
    """
    # Get saved options
    get_option: Callable[[str], str | int | float | None] = partial(
        options.get_tool_option, "curve_distribute_vertices"
    )
    # Create the window
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    cmds.window(
        WINDOW,
        width=240,
        height=100,
        title=f"ZenTools: {CURVE_DISTRIBUTE_BETWEEN_VERTICES_LABEL} Options",
    )
    column_layout: str = cmds.columnLayout(
        adjustableColumn=True, parent=WINDOW, columnAlign="left", margins=15
    )
    selected: int = 1
    with contextlib.suppress(ValueError):
        selected = ("UNIFORM", "PROPORTIONAL").index(
            get_option(  # type: ignore
                "distribution_type", DistributionType.UNIFORM
            )
        ) + 1
    cmds.radioButtonGrp(
        DISTRIBUTION_TYPE_RADIO_BUTTON,
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
    cmds.showWindow(WINDOW)


def do_curve_distribute_vertices() -> None:
    """
    Execute `loop`, getting arguments from the UI or saved options
    """
    kwargs: dict[str, float | bool | str] = options.get_tool_options(
        "curve_distribute_vertices"
    )
    curve_distribute_vertices(**kwargs)  # type: ignore
