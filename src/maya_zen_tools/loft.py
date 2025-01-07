from __future__ import annotations

import contextlib
from functools import partial
from typing import Callable, Iterable, Sequence

from maya import cmds  # type: ignore

from maya_zen_tools import options
from maya_zen_tools._create import create_edges_rebuild_curve
from maya_zen_tools._traverse import (
    find_end_vertex,
    get_shared_edge_vertices,
    get_shared_vertex_edges,
    iter_edges_vertices,
    iter_selected_components,
    iter_shortest_vertices_path_proportional_positions,
    iter_shortest_vertices_path_uniform_positions,
    iter_sort_vertices_by_distance,
    iter_sorted_vertices,
    iter_vertices_edges,
)
from maya_zen_tools._ui import WINDOW
from maya_zen_tools.errors import NonContiguousMeshSelectionError
from maya_zen_tools.menu import LOFT_DISTRIBUTE_VERTICES_BETWEEN_EDGES_LABEL


def _get_contiguous_edges_terminal_vertices(
    edges: Sequence[str],
) -> tuple[str, str]:
    """
    Get the vertices at the start and end of the given sequence
    of contiguous edges.
    """
    if len(edges) == 1:
        # Both edge vertices are ends
        return tuple(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    *edges, fromEdge=True, toVertex=True
                ),
                flatten=True,
            )[:2]
        )
    return (
        (
            set(
                cmds.ls(
                    *cmds.polyListComponentConversion(
                        edges[0], fromEdge=True, toVertex=True
                    ),
                    flatten=True,
                )
            )
            - set(
                cmds.ls(
                    *cmds.polyListComponentConversion(
                        edges[1], fromEdge=True, toVertex=True
                    ),
                    flatten=True,
                )
            )
        ).pop(),
        (
            set(
                cmds.ls(
                    *cmds.polyListComponentConversion(
                        edges[-1], fromEdge=True, toVertex=True
                    ),
                    flatten=True,
                )
            )
            - set(
                cmds.ls(
                    *cmds.polyListComponentConversion(
                        edges[-2], fromEdge=True, toVertex=True
                    ),
                    flatten=True,
                )
            )
        ).pop(),
    )


def _get_rotated_vertex_loop(
    vertices: tuple[str, ...], terminal_vertex: str
) -> tuple[str, ...]:
    """
    Rotate a (closed) vertex loop so the `terminal_vertex` is the first
    and last vertex in the loop.
    """
    if vertices[0] == terminal_vertex:
        return vertices
    index: int = vertices.index(terminal_vertex)
    return (
        # Vertex loops start and end with the same vertex, so we drop the last
        # item when rotating, then include the terminal vertex at both the
        # start and end
        vertices[index:-1] + vertices[: index + 1]
    )


def _iter_directionally_aligned_vertex_loops(
    vertex_loops: Sequence[tuple[str, ...]],
) -> Iterable[tuple[str, ...]]:
    """
    Given a series of vertex loops, reverse where needed to make them all
    sorted in the same direction
    """
    reference_vertex: str = vertex_loops[0][1]
    yield vertex_loops[0]
    vertex_loop: tuple[str, ...]
    for vertex_loop in vertex_loops:
        penterminus_vertices: tuple[str, str] = (
            vertex_loop[1],
            vertex_loop[-2],
        )
        if (
            tuple(
                iter_sort_vertices_by_distance(
                    reference_vertex, set(penterminus_vertices)
                )
            )
            == penterminus_vertices
        ):
            yield vertex_loop
        else:
            # Since the next-to-last vertex was closed than the second
            # vertex to the reference, we need to reverse the loop
            yield tuple(reversed(vertex_loop))


def _iter_align_closed_loop_contiguous_edges(
    edge_loops: list[list[str]],
) -> Iterable[tuple[str, ...]]:
    """
    This function yields sorted and aligned rearrangements of the (closed)
    edge loops provided as input.
    """
    if len(edge_loops) == 1:
        yield from map(tuple, edge_loops)
        return
    edge_loop: list[str]
    vertex_loops: list[tuple[str, ...]] = [
        tuple(iter_edges_vertices(edge_loop)) for edge_loop in edge_loops
    ]
    # Find a corner vertex by getting the furthest vertex from the first start
    # vertex
    other_vertices: set[str] = set()
    vertex_loop: tuple[str, ...]
    for vertex_loop in vertex_loops[1:]:
        other_vertices |= set(vertex_loop)
    # Finding the vertex the furthest from any in one of our loops would work,
    # but we can marginaslly reduce overhead by use a known endpoint and
    # excluding the vertices in that end points looop
    origin_vertex: str = find_end_vertex(
        other_vertices, origin_vertex=vertex_loops[0][0]
    )
    vertex_loop_sets: tuple[set[str], ...] = tuple(map(set, vertex_loops))
    unused_loop_indices: set[int] = set(range(len(vertex_loops)))
    # Now we will find the closest vertex to the origin on each other loop,
    # and align the vertex loops so that each begins/ends with that vertex
    vertices: set[str] = {origin_vertex}
    sorted_vertex_loops: list[tuple[str, ...]] = []
    while unused_loop_indices:
        index: int
        for index in tuple(unused_loop_indices):
            matched_vertices: set[str] = vertices & vertex_loop_sets[index]
            if matched_vertices:
                sorted_vertex_loops.append(
                    _get_rotated_vertex_loop(
                        vertex_loops[index], matched_vertices.pop()
                    )
                )
                unused_loop_indices.remove(index)
                break
        if unused_loop_indices:
            shared_edge_vertices: set = get_shared_edge_vertices(vertices)
            if not shared_edge_vertices:
                # If there are loops unconsumed, but we can't grow the
                # vertex selection any further, the mesh is likely not
                # contiguous
                raise NonContiguousMeshSelectionError(edge_loops)
            vertices |= shared_edge_vertices
    for vertex_loop in _iter_directionally_aligned_vertex_loops(
        sorted_vertex_loops
    ):
        yield tuple(iter_vertices_edges(vertex_loop))


def _iter_aligned_contiguous_edges(
    *selected_edges: str,
) -> Iterable[tuple[str, ...]]:
    edge_loop_segments: list[list[str]] = list(
        _iter_contiguous_edges(*selected_edges)
    )
    if (
        len(edge_loop_segments[0]) > 2  # noqa: PLR2004
        and edge_loop_segments[0][0] != edge_loop_segments[0][-1]
        and cmds.polyListComponentConversion(
            edge_loop_segments[0][0],
            edge_loop_segments[0][-1],
            toVertex=True,
            fromEdge=True,
            internal=True,
        )
    ):
        # If the first and last edges share a vertex, the edges form a closed
        # loop, so we require an alternate alignment strategy
        yield from _iter_align_closed_loop_contiguous_edges(edge_loop_segments)
        return
    # Get the start and end vertices for each segment
    origin_vertex: str | None = None
    segment_terminal_vertices: tuple[str, ...]
    start_vertices_edges: dict[str, tuple[str, ...]] = {}
    for index, segment_terminal_vertices in enumerate(
        map(_get_contiguous_edges_terminal_vertices, edge_loop_segments)
    ):
        if origin_vertex is None:
            start_vertices_edges[segment_terminal_vertices[0]] = tuple(
                edge_loop_segments[index]
            )
            # This vertex will be used to align subsequent segments
            origin_vertex = segment_terminal_vertices[0]
        else:
            sorted_segment_terminal_vertices: tuple[str, ...] = tuple(
                iter_sort_vertices_by_distance(
                    origin_vertex, set(segment_terminal_vertices)
                )
            )
            start_vertices_edges[sorted_segment_terminal_vertices[0]] = tuple(
                edge_loop_segments[index]
                if (
                    sorted_segment_terminal_vertices
                    == segment_terminal_vertices
                )
                # If the terminal vertices changed order when sorted, the
                # segment was inverted, so we reverse it
                else reversed(edge_loop_segments[index])
            )
    # Sort the edge loops
    start_vertex: str
    for start_vertex in iter_sorted_vertices(start_vertices_edges.keys()):
        yield start_vertices_edges[start_vertex]


def _iter_contiguous_edges(  # noqa: C901
    *selected_edges: str,
) -> Iterable[list[str]]:
    """
    Yield tuples of contiguous edge loop segments.

    Parameters:
        selected_edges: Two or more edge loop segments comprised of equal
            numbers edges each, with ends alignged along perpendicular
            edge loops forming a rectangular section of a mesh.
    """
    edges: set[str] = set(selected_edges)
    edge_loop_segments: list[list[str]] = []
    edge_loop_segment: list[str]
    # Organize edges into contiguous segments
    while edges:
        edge: str = edges.pop()
        adjacent_edges: set[str] = set(get_shared_vertex_edges({edge}))
        # This is a list of edge loop segment indices where the edge could be
        # appended. Since two segments could be matched for the same edge,
        # we need to retain this as a list.
        found: int | None = None
        index: int
        for index, edge_loop_segment in enumerate(edge_loop_segments):
            if not edge_loop_segment:
                continue
            if edge_loop_segment[0] in adjacent_edges:
                # This edge is adjacent to the first edge in the segment
                if found is None:
                    edge_loop_segment.insert(0, edge)
                    found = index
                    # Keep looking to see if there is a second match
                    continue
                else:
                    if edge == edge_loop_segments[found][-1]:
                        edge_loop_segments[found].extend(edge_loop_segment)
                    else:
                        edge_loop_segments[found] = (
                            list(reversed(edge_loop_segment))
                            + edge_loop_segments[found]
                        )
                    edge_loop_segment.clear()
                    break
            if edge_loop_segment[-1] in adjacent_edges:
                # This edge is adjacent to the last edge in the segment
                if found is None:
                    edge_loop_segment.append(edge)
                    found = index
                    # Keep looking to see if there is a second match
                    continue
                else:
                    if edge == edge_loop_segments[found][-1]:
                        edge_loop_segments[found].extend(
                            reversed(edge_loop_segment)
                        )
                    else:
                        edge_loop_segments[found] = (
                            list(edge_loop_segment) + edge_loop_segments[found]
                        )
                    edge_loop_segment.clear()
                    break
        if found is None:
            # This edge is not adjacent to any segments started thus far
            edge_loop_segments.append([edge])
    # Remove the cleared segments (they've been joined with another)
    yield from filter(None, edge_loop_segments)


def _rebuild_surface_distribute_vertices_between_edges(
    rebuild_surface: str,
    edge_loops: tuple[tuple[str, ...], ...],
    distribution_type: str = options.DistributionType.UNIFORM,
) -> set[str]:
    """
    Given a rebuildSurface node and one or more edge loops, distribute all
    vertices between the edge loops along the surface, and return the
    vertices as a set.
    """
    point_on_surface_info: str = cmds.createNode("pointOnSurfaceInfo")
    cmds.connectAttr(
        f"{rebuild_surface}.outputSurface",
        f"{point_on_surface_info}.inputSurface",
    )
    edges: tuple[str, ...]
    vertex_loops: tuple[tuple[str, ...], ...] = tuple(
        tuple(iter_edges_vertices(edges)) for edges in edge_loops
    )
    progress_window: str = cmds.progressWindow(
        maxValue=len(vertex_loops[0]),
    )
    v_position: float
    selected_vertices: tuple[str, ...]
    vertices: set[str] = set()
    for v_position, selected_vertices in enumerate(zip(*vertex_loops)):
        cmds.setAttr(f"{point_on_surface_info}.parameterV", v_position)
        u_position: float
        vertex: str
        for vertex, u_position in (
            iter_shortest_vertices_path_proportional_positions(
                selected_vertices
            )
            if distribution_type == options.DistributionType.PROPORTIONAL
            else iter_shortest_vertices_path_uniform_positions(
                selected_vertices
            )
        ):
            cmds.setAttr(f"{point_on_surface_info}.parameterU", u_position)
            position: tuple[float, float, float] = cmds.getAttr(
                f"{point_on_surface_info}.position"
            )[0]
            cmds.move(*position, vertex, absolute=True, worldSpace=True)
            vertices.add(vertex)
        cmds.progressWindow(progress_window, progress=v_position)
    cmds.progressWindow(progress_window, endProgress=True)
    return vertices


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
    edge_loops: tuple[tuple[str, ...], ...] = tuple(
        _iter_aligned_contiguous_edges(*selected_edges)
    )
    cmds.waitCursor(state=True)
    index: int
    edge_loop: tuple[str, ...]
    loft: str = cmds.createNode("loft", name="loftBetweenEdges#")
    for index, edge_loop in enumerate(edge_loops):
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
    cmds.setAttr(f"{rebuild_surface}.spansU", len(edge_loops) - 1)
    cmds.setAttr(f"{rebuild_surface}.spansV", len(edge_loops[0]))
    cmds.setAttr(f"{rebuild_surface}.keepRange", 2)
    cmds.setAttr(f"{rebuild_surface}.endKnots", 1)
    cmds.setAttr(f"{rebuild_surface}.direction", 0)
    vertices: set[str] = _rebuild_surface_distribute_vertices_between_edges(
        rebuild_surface=rebuild_surface,
        edge_loops=edge_loops,
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
