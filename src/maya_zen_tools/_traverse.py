from __future__ import annotations

from collections import deque
from typing import Iterable

from maya import cmds  # type: ignore

from maya_zen_tools.errors import (
    InvalidSelectionError,
    NonContiguousMeshSelectionError,
    TooManyShapesError,
)


def iter_vertex_edge_ids(vertex: str) -> Iterable[int]:
    """
    Given a vertex, yield adjacent edge IDs
    """
    yield from map(
        get_component_id,
        cmds.ls(
            *cmds.polyListComponentConversion(
                vertex, fromVertex=True, toEdge=True
            ),
            flatten=True,
        ),
    )


def get_expanded_vertices(vertices: set[str]) -> set[str]:
    """
    Given one or more vertices, return these vertices, plus all vertices
    connected by an edge.
    """
    return set(
        cmds.ls(
            *cmds.polyListComponentConversion(
                *cmds.polyListComponentConversion(
                    *vertices, fromVertex=True, toEdge=True
                ),
                fromEdge=True,
                toVertex=True,
            ),
            flatten=True,
        )
    )


def get_bordering_vertices(vertices: set[str]) -> set[str]:
    """
    Given one or more vertices, return all vertices connected to the
    input vertices by an edge (excluded all input vertices).
    """
    return get_expanded_vertices(vertices) - vertices


def iter_sort_vertices_by_distance(
    origin_vertex: str, other_vertices: set[str]
) -> Iterable[str]:
    vertices: set[str] = {origin_vertex}
    bordering_vertices: set[str]
    matched_vertices: set[str]
    while other_vertices:
        bordering_vertices = get_bordering_vertices(vertices)
        if not bordering_vertices:
            # If there are no bordering vertices, any remaining vertices
            # must belong to a part of the mesh which cannot be reached
            # by edge traversal, and is therefore disconnected
            raise NonContiguousMeshSelectionError(
                set(origin_vertex) | other_vertices
            )
        matched_vertices = bordering_vertices & other_vertices
        if matched_vertices:
            yield from matched_vertices
            other_vertices -= matched_vertices
            if not other_vertices:
                return
        # Add the bordering vertices to our traversal selection
        vertices |= bordering_vertices


def find_end_vertex(vertices: Iterable[str]) -> str:
    """
    Given a selection of vertices, find *one* of the end vertices
    """
    other_vertices: set[str] = set(vertices)
    origin_vertex: str = other_vertices.pop()
    if len(other_vertices) == 1:
        # If there are fewer than 3 vertices, either will be an end vertex
        return other_vertices.pop()
    if not other_vertices:
        return origin_vertex
    # Given any vertex on an edge loop, the most distance vertex will
    # always be one of the end vertices
    return deque(
        iter_sort_vertices_by_distance(origin_vertex, other_vertices), maxlen=1
    )[-1]


def iter_sorted_edge_loop_vertices(vertices: Iterable[str]) -> Iterable[str]:
    """
    Given a set of vertices along an edge loop, yield the vertices in
    order from one end to the other (which end starts is not guaranteed, so
    this should only be used where the direction does not matter).

    Parameters:
        vertices: A sequence of vertices along an edge loop.
    """
    other_vertices: set[str] = set(vertices)
    end_vertex: str = find_end_vertex(other_vertices)
    other_vertices.remove(end_vertex)
    yield end_vertex
    yield from iter_sort_vertices_by_distance(end_vertex, other_vertices)


def get_component_id(component: str) -> int:
    """
    Given a component name, return the integer ID.
    """
    return int(component.rpartition("[")[-1].rpartition("]")[0])


def get_components_shape(components: Iterable[str]) -> str:
    """
    Given a set of components, return the shape name, or raise an error
    if there is more than one shape
    """
    shapes: list[str] = cmds.ls(*components, objectsOnly=True, flatten=True)
    if len(shapes) > 1:
        raise TooManyShapesError(shapes)
    if not shapes:
        raise InvalidSelectionError(components)
    return shapes[0]


def get_shape_transform(shape: str) -> str:
    """
    Get the associated transform node for a shape
    """
    return cmds.listRelatives(shape, parent=True, path=True)[0]
