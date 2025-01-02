from __future__ import annotations

from collections import deque
from typing import Iterable, Sequence

from maya import cmds  # type: ignore

from maya_zen_tools.errors import (
    InvalidSelectionError,
    NonContiguousMeshSelectionError,
    TooManyShapesError,
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


def get_expanded_uvs(uvs: set[str]) -> set[str]:
    """
    Given one or more UVs, return these UVs, plus all UVs
    connected by an edge.
    """
    return set(
        cmds.ls(
            *cmds.polyListComponentConversion(
                *cmds.polyListComponentConversion(
                    *uvs, fromUV=True, toEdge=True
                ),
                fromEdge=True,
                toUV=True,
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


def get_bordering_uvs(uvs: set[str]) -> set[str]:
    """
    Given one or more vertices, return all vertices connected to the
    input vertices by an edge (excluded all input vertices).
    """
    return get_expanded_vertices(uvs) - uvs


def iter_sort_vertices_by_distance(
    origin_vertex: str, other_vertices: set[str]
) -> Iterable[str]:
    """
    Given an origin vertex and a set of other vertices, yield the other
    vertices by their distance from the origin.

    Parameters:
        origin_vertex: The vertex to use as an origin for sorting.
        other_vertices: The vertices to be sorted.
    """
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


def iter_sort_uvs_by_distance(
    origin_uv: str, other_uvs: set[str]
) -> Iterable[str]:
    """
    Given an origin UV and a set of other UVs, yield the other
    UVs by their distance from the origin.

    Parameters:
        origin_uv: The vertex to use as an origin for sorting.
        other_uvs: The vertices to be sorted.
    """
    uvs: set[str] = {origin_uv}
    bordering_uvs: set[str]
    matched_uvs: set[str]
    while other_uvs:
        bordering_uvs = get_bordering_uvs(uvs)
        if not bordering_uvs:
            # If there are no bordering UVs, any remaining UVs
            # must belong to a part of the mesh which cannot be reached
            # by edge traversal, and is therefore disconnected
            raise NonContiguousMeshSelectionError(set(origin_uv) | other_uvs)
        matched_uvs = bordering_uvs & other_uvs
        if matched_uvs:
            yield from matched_uvs
            other_uvs -= matched_uvs
            if not other_uvs:
                return
        # Add the bordering UVs to our traversal selection
        uvs |= bordering_uvs


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


def find_end_uv(uvs: Iterable[str]) -> str:
    """
    Given a selection of UVs, find *one* of the end UVs
    """
    other_uvs: set[str] = set(uvs)
    origin_uv: str = other_uvs.pop()
    if len(other_uvs) == 1:
        # If there are fewer than 3 UVs, either will be an end vertex
        return other_uvs.pop()
    if not other_uvs:
        return origin_uv
    # Given any UV on an edge loop, the most distant UV will
    # always be one of the end UVs
    return deque(iter_sort_uvs_by_distance(origin_uv, other_uvs), maxlen=1)[-1]


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


def iter_sorted_edge_loop_uvs(uvs: Iterable[str]) -> Iterable[str]:
    """
    Given a set of UVs along an edge loop, yield the UVs in
    order from one end to the other (which end starts is not guaranteed, so
    this should only be used where the direction does not matter).

    Parameters:
        uvs: A sequence of UVs along an edge loop.
    """
    other_uvs: set[str] = set(uvs)
    end_uv: str = find_end_vertex(other_uvs)
    other_uvs.remove(end_uv)
    yield end_uv
    yield from iter_sort_vertices_by_distance(end_uv, other_uvs)


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


def iter_selected_components(
    *component_types: str, selection: Sequence[str] = ()
) -> Iterable[str]:
    """
    Yield selected components, in selection order.

    Parameters:
        component_types: vtx | e | map | vertex | edge | uv
        selection: A flat selection sequence. If not provided,
            `maya.cmds.ls` will be used.
    """
    component_type: str
    component_types: set[str] = {
        "vtx"
        if component_type == "vertex"
        else "e"
        if component_type == "edge"
        else "map"
        if component_type == "uv"
        else component_type
        for component_type in component_types
    }
    selected: str
    component: str
    selected_object: str
    for selected in selection or cmds.ls(orderedSelection=True, flatten=True):
        selected_object, component = selected.rpartition(".")[::2]
        if not selected_object and component:
            continue
        component_type = component.rpartition("[")[0]
        if component_type and (component_type in component_types):
            yield selected
