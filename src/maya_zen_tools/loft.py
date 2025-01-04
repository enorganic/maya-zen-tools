from __future__ import annotations

from typing import Iterable, Sequence

from maya import cmds  # type: ignore

from maya_zen_tools._traverse import (
    get_shared_vertex_edges,
    iter_sort_vertices_by_distance,
    iter_sorted_vertices,
)


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


def _iter_contiguous_edges(
    *selected_edges: str,
) -> Iterable[tuple[str, ...]]:
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
        found: bool = False
        for edge_loop_segment in edge_loop_segments:
            if edge_loop_segment[0] in adjacent_edges:
                # This edge is adjacent to the first edge in the segment
                edge_loop_segment.insert(0, edge)
                found = True
                break
            if edge_loop_segment[-1] in adjacent_edges:
                # This edge is adjacent to the last edge in the segment
                edge_loop_segment.append(edge)
                found = True
                break
        if not found:
            # This edge is not adjacent to any segments started thus far
            edge_loop_segments.append([edge])
    # Get the start and end vertices for each segment
    origin_vertex: str | None = None
    segment_terminal_vertices: tuple[str, ...]
    start_vertices_edges: dict[str, tuple[str, ...]] = {}
    index: int
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
            print("!!!", sorted_segment_terminal_vertices)
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


# def loft_distribute_between_edges(
#     *selected_edges: str,
#     distribution_type: str = options.DistributionType.UNIFORM,
# ) -> set[str]:
#     """
#     Given a selection of edge loop segments, aligned parallel to one
#     another on a polygon mesh, distribute the vertices sandwiched between
#     along a loft.
#     """
#     return set()
