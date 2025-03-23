from __future__ import annotations

from collections import deque
from functools import cache
from itertools import chain, islice
from math import sqrt
from typing import Iterable, Sequence

from maya import cmds  # type: ignore

from maya_zen_tools.errors import (
    InvalidSelectionError,
    NonContiguousMeshSelectionError,
    NonLinearSelectionError,
    TooManyShapesError,
)


def add_shared_vertex_edges(edges: set[str]) -> set[str]:
    """
    Given one or more edges, return these edges, plus all edges
    sharing a vertex with the input edges.
    """
    return set(
        cmds.ls(
            *cmds.polyListComponentConversion(
                *cmds.polyListComponentConversion(
                    *edges, fromEdge=True, toVertex=True
                ),
                fromVertex=True,
                toEdge=True,
            ),
            flatten=True,
        )
    )


def add_shared_uv_edges(edges: set[str]) -> set[str]:
    """
    Given one or more edges, return these edges, plus all edges
    sharing a UV with the input edges.
    """
    return set(
        cmds.ls(
            *cmds.polyListComponentConversion(
                *cmds.polyListComponentConversion(
                    *edges, fromEdge=True, toUV=True
                ),
                fromUV=True,
                toEdge=True,
            ),
            flatten=True,
        )
    )


def get_shared_vertex_edges(edges: set[str]) -> set[str]:
    """
    Given one or more edges, return all edges
    sharing a vertex with the input edges.
    """
    return add_shared_vertex_edges(edges) - edges


def get_shared_uv_edges(edges: set[str]) -> set[str]:
    """
    Given one or more edges, return all edges
    sharing a UV with the input edges.
    """
    return add_shared_uv_edges(edges) - edges


def add_shared_edge_vertices(vertices: set[str]) -> set[str]:
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


def add_shared_face_edge_uvs(uvs: set[str]) -> set[str]:
    """
    Given one or more UVs, return these UVs, plus all UVs
    connected by an edge *and* a face.
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
    ) & set(
        cmds.ls(
            *cmds.polyListComponentConversion(
                *cmds.polyListComponentConversion(
                    *uvs, fromUV=True, toFace=True
                ),
                toFace=True,
                toUV=True,
            ),
            flatten=True,
        )
    )


def get_shared_edge_vertices(vertices: set[str]) -> set[str]:
    """
    Given one or more vertices, return all vertices connected to the
    input vertices by an edge.
    """
    return add_shared_edge_vertices(vertices) - vertices


def get_shared_face_edge_uvs(uvs: set[str]) -> set[str]:
    """
    Given one or more UVs, return all UVs connected to the
    input UVs by an edge *and* a face.
    """
    return add_shared_face_edge_uvs(uvs) - uvs


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
    unsorted_vertices: set[str] = set(other_vertices) - {origin_vertex}
    while unsorted_vertices:
        bordering_vertices = get_shared_edge_vertices(vertices)
        if not bordering_vertices:
            # If there are no bordering vertices, any remaining vertices
            # must belong to a part of the mesh which cannot be reached
            # by edge traversal, and is therefore disconnected
            raise NonContiguousMeshSelectionError(
                origin_vertex, other_vertices
            )
        matched_vertices = bordering_vertices & unsorted_vertices
        if matched_vertices:
            yield from matched_vertices
            unsorted_vertices -= matched_vertices
            if not unsorted_vertices:
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
        bordering_uvs = get_shared_face_edge_uvs(uvs)
        if not bordering_uvs:
            # If there are no bordering UVs, any remaining UVs
            # must belong to a part of the mesh which cannot be reached
            # by edge traversal, and is therefore disconnected
            raise NonContiguousMeshSelectionError({origin_uv} | other_uvs)
        matched_uvs = bordering_uvs & other_uvs
        if matched_uvs:
            yield from matched_uvs
            other_uvs -= matched_uvs
            if not other_uvs:
                return
        # Add the bordering UVs to our traversal selection
        uvs |= bordering_uvs


def find_end_vertex(vertices: Iterable[str], origin_vertex: str = "") -> str:
    """
    Given a selection of vertices, find *one* of the end vertices
    """
    other_vertices: set[str] = set(vertices)
    if not origin_vertex:
        origin_vertex = other_vertices.pop()
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


def find_end_uv(uvs: Iterable[str], origin_uv: str = "") -> str:
    """
    Given a selection of UVs, find *one* of the end UVs
    """
    other_uvs: set[str] = set(uvs)
    if not origin_uv:
        origin_uv = other_uvs.pop()
    if len(other_uvs) == 1:
        # If there are fewer than 3 UVs, either will be an end vertex
        return other_uvs.pop()
    if not other_uvs:
        return origin_uv
    # Given any UV on an edge loop, the most distant UV will
    # always be one of the end UVs
    return deque(iter_sort_uvs_by_distance(origin_uv, other_uvs), maxlen=1)[-1]


def iter_sorted_contiguous_vertices(vertices: Iterable[str]) -> Iterable[str]:
    """
    Given a set of vertices along an edge loop, yield the vertices in
    order from one end to the other (which end starts is not guaranteed, so
    this should only be used where the direction does not matter).

    Note: This works with closed loops, whereas `iter_sorted_vertices`
    does not.

    Parameters:
        vertices: A sequence of vertices along an edge loop.
    """
    vertices = set(vertices)
    vertex: str = find_end_vertex(vertices)
    vertices.remove(vertex)
    yield vertex
    while vertices:
        vertex = (get_shared_edge_vertices({vertex}) & vertices).pop()
        vertices.remove(vertex)
        yield vertex


def iter_sorted_contiguous_edges(edges: Iterable[str]) -> Iterable[str]:
    """
    Given a set of contiguous edges, yield the edges in
    order from one end to the other (which end starts is not guaranteed, so
    this should only be used where the direction does not matter).

    Parameters:
        edges: Two or more contiguous edges
    """
    edges = set(edges)
    edge: str
    for edge in iter_vertices_edges(
        iter_sorted_contiguous_vertices(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    *edges, fromEdge=True, toVertex=True
                ),
                flatten=True,
            )
        )
    ):
        yield edge
        edges.remove(edge)
    # If the edges formed a closed loop, there will be one more remaining
    yield from edges


def iter_sorted_contiguous_uvs(uvs: Iterable[str]) -> Iterable[str]:
    """
    Given a set of contiguous UVs along an edge loop, yield the UVs in
    order from one end to the other (which end starts is not guaranteed, so
    this should only be used where the direction does not matter).

    Note: This works with closed loops, whereas `iter_sorted_uvs`
    does not.

    Parameters:
        uvs: A sequence of UVs along an edge loop.
    """
    uvs = set(uvs)
    uv: str = find_end_vertex(uvs)
    uvs.remove(uv)
    yield uv
    while uvs:
        uv = (get_shared_face_edge_uvs({uv}) & uvs).pop()
        uvs.remove(uv)
        yield uv


def iter_sorted_vertices(vertices: Iterable[str]) -> Iterable[str]:
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


def iter_sorted_uvs(uvs: Iterable[str]) -> Iterable[str]:
    """
    Given a set of UVs along an edge loop, yield the UVs in
    order from one end to the other (which end starts is not guaranteed, so
    this should only be used where the direction does not matter).

    Parameters:
        uvs: A sequence of UVs along an edge loop.
    """
    other_uvs: set[str] = set(uvs)
    end_uv: str = find_end_uv(other_uvs)
    other_uvs.remove(end_uv)
    yield end_uv
    yield from iter_sort_uvs_by_distance(end_uv, other_uvs)


def get_component_id(component: str) -> int:
    """
    Given a component name, return the integer ID.
    """
    return int(component.rpartition("[")[-1].rpartition("]")[0])


def get_component_shape(component: str) -> str | None:
    """
    If `selection` is a polygon component, return the shape,
    otherwise, return `None`.
    """
    shape: str
    component_type: str
    shape, component_type = component.partition("[")[0].rpartition(".")[::2]
    return (
        shape
        if component_type in {"vtx", "map", "e", "vtxFace", "f"}
        else None
    )


def get_components_shape(components: Iterable[str]) -> str:
    """
    Given a set of components, return the shape name, or raise an error
    if there is more than one shape
    """
    shapes: set[str] = set(filter(None, map(get_component_shape, components)))
    if len(shapes) > 1:
        raise TooManyShapesError(tuple(sorted(shapes)))
    if not shapes:
        raise InvalidSelectionError(components)
    return shapes.pop()


def get_shape_transform(shape: str) -> str:
    """
    Get the associated transform node for a shape
    """
    return cmds.listRelatives(shape, parent=True, path=True)[0]


def get_transform_shape(transform: str) -> str:
    """
    Get the first associated shape node for a transorm
    """
    child: str
    return next(
        child
        for child in iter(
            cmds.listRelatives(transform, children=True, path=True),
        )
        if cmds.nodeType(child) != "transform"
    )


def iter_selected_components(
    *component_types: str, selection: Sequence[str] = ()
) -> Iterable[str]:
    """
    Yield selected components, in selection order.

    Parameters:
        component_types: vtx | e | map | vtxFace | f
        selection: A flat selection sequence. If not provided,
            `maya.cmds.ls` will be used.
    """
    component_type: str
    component_types_: set[str] = set(component_types)
    selected: str
    component: str
    selected_object: str
    for selected in selection or cmds.ls(orderedSelection=True, flatten=True):
        selected_object, component = selected.rpartition(".")[::2]
        if not selected_object and component:
            continue
        component_type = component.rpartition("[")[0]
        if component_type and (component_type in component_types_):
            yield selected


def get_uvs_shared_edge(*uvs: str) -> str:
    """
    Get the edge shared by two or more UVs
    """
    uv: str
    shared_edges: set | None = None
    for uv in uvs:
        uv_edges: set[str] = set(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    uv, fromUV=True, toEdge=True
                ),
                flatten=True,
            )
        )
        if shared_edges is None:
            shared_edges = uv_edges
        else:
            shared_edges &= uv_edges
    if not shared_edges:
        raise NonLinearSelectionError(uvs)
    return shared_edges.pop()


def iter_uvs_edges(uvs: Iterable[str]) -> Iterable[str]:
    """
    Yield the edges between a series of ordered UVs, in the same
    order as the UVs
    """
    uvs = iter(uvs)
    try:
        start_uv: str = next(uvs)
    except StopIteration:
        return
    end_uv: str
    for end_uv in uvs:
        yield get_uvs_shared_edge(start_uv, end_uv)
        start_uv = end_uv


def iter_vertices_edges(vertices: Iterable[str]) -> Iterable[str]:
    """
    Yield the edges between a series of ordered vertices, in the same
    order as the vertices
    """
    vertices = iter(vertices)
    try:
        start_vertex: str = next(vertices)
    except StopIteration:
        return
    end_vertex: str
    for end_vertex in vertices:
        yield from cmds.polyListComponentConversion(
            start_vertex,
            end_vertex,
            fromVertex=True,
            toEdge=True,
            internal=True,
        )
        start_vertex = end_vertex


def iter_edges_vertices(edges: Iterable[str]) -> Iterable[str]:
    """
    Yield the vertices between a series of ordered edges, in the same
    order as the edges
    """
    edges = iter(edges)
    previous_vertices: set[str] | None = None
    edge: str
    for edge in edges:
        vertices: set[str] = set(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    edge,
                    fromEdge=True,
                    toVertex=True,
                ),
                flatten=True,
            )
        )
        if previous_vertices is not None:
            yield from previous_vertices - vertices
            yield from previous_vertices & vertices
            previous_vertices = vertices - previous_vertices
        else:
            previous_vertices = vertices
    yield from (previous_vertices or ())


def iter_edges_uvs(edges: Iterable[str]) -> Iterable[str]:
    """
    Yield the UVs between a series of ordered edges, in the same
    order as the edges
    """
    edges = iter(edges)
    previous_uvs: set[str] | None = None
    edge: str
    for edge in edges:
        uvs: set[str] = set(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    edge,
                    fromEdge=True,
                    toUV=True,
                ),
                flatten=True,
            )
        )
        if previous_uvs is not None:
            yield from previous_uvs - uvs
            yield from previous_uvs & uvs
            previous_uvs = uvs - previous_uvs
        else:
            previous_uvs = uvs
    yield from (previous_uvs or ())


def get_distance_between(
    position_a: tuple[float, ...],
    position_b: tuple[float, ...],
    *args: tuple[float, ...],
) -> float:
    """
    Get the (total) distance between two or more 3d or 2d coordinates
    """
    a: float
    b: float
    distance: float = sqrt(
        sum(abs(a - b) ** 2 for a, b in zip(position_a, position_b))
    )
    if args:
        return distance + get_distance_between(position_b, *args)
    return distance


def get_least_deviant_midpoint_vertex(
    start_point_position: tuple[float, float, float],
    end_point_position: tuple[float, float, float],
    midpoint_vertices: Iterable[str],
) -> str:
    """
    Get the vertex with coordinates which deviate least from the line
    connecting a start and end point position.
    """
    least_deviant_vertex: str = ""
    least_deviant_length: float = 0.0
    vertex: str
    for vertex in midpoint_vertices:
        length: float = get_distance_between(
            start_point_position,
            cmds.pointPosition(vertex),
            end_point_position,
        )
        if (not least_deviant_vertex) or (length < least_deviant_length):
            least_deviant_length = length
            least_deviant_vertex = vertex
    return least_deviant_vertex


def get_least_deviant_midpoint_uv(
    start_point_position: tuple[float, float],
    end_point_position: tuple[float, float],
    midpoint_uvs: Iterable[str],
) -> str:
    """
    Get the UV with coordinates which deviate least from the line
    connecting a start and end point positions.
    """
    least_deviant_uv: str = ""
    least_deviant_length: float = 0.0
    uv: str
    for uv in midpoint_uvs:
        length: float = get_distance_between(
            start_point_position,
            tuple(cmds.polyEditUV(uv, query=True)),
            end_point_position,
        )
        if (not least_deviant_uv) or (length < least_deviant_length):
            least_deviant_length = length
            least_deviant_uv = uv
    return least_deviant_uv


def iter_shortest_vertex_path(
    start_vertex: str, end_vertex: str
) -> Iterable[str]:
    """
    Get a the vertex path connected by the fewest possible number of edges by
    intersecting expanding rings of vertices from either end.

    Parameters:
        start_vertex: The vertex at the start of the path.
        end_vertex: The vertex at the end of the path.
    """

    @cache
    def get_start_point_position() -> tuple[float, float, float]:
        return tuple(cmds.pointPosition(start_vertex))

    @cache
    def get_end_point_position() -> tuple[float, float, float]:
        return tuple(cmds.pointPosition(end_vertex))

    start_vertex_rings: list[set[str]] = [{start_vertex}]
    end_vertex_rings: list[set[str]] = [{end_vertex}]
    # Getting the component shape is done early
    # in order to raise an error if the vertices are not on the same shape,
    # but is also used when raising an error, and for use with the polySelect
    # command
    shape: str = get_components_shape((start_vertex, end_vertex))
    vertices: set[str] = {start_vertex}
    expanded_vertices: set[str]
    ring_vertices: set[str]
    # Get a set of rings grown from the start vertex
    while end_vertex not in vertices:
        expanded_vertices = add_shared_edge_vertices(vertices)
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
        expanded_vertices = add_shared_edge_vertices(vertices)
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
        # There will typically be only one intersecting vertex, however
        # when there is more than one shortest (having the least edges)
        # path between the vertices, we need to make sure that the path
        # we choose is contiguous. When multiple contiguous options for
        # traversal exist, we choose the one which is most nearly aligned
        # with the vector between the start and end vertices.
        if vertex and len(ring_intersection) > 1:
            # Intersect with only the vertices adjacent to the previously
            # yielded vertex
            ring_intersection &= add_shared_edge_vertices({vertex})
        if len(ring_intersection) > 1:
            vertex = get_least_deviant_midpoint_vertex(
                get_start_point_position(),
                get_end_point_position(),
                ring_intersection,
            )
        else:
            vertex = ring_intersection.pop()
        yield vertex


def iter_shortest_uv_path(start_uv: str, end_uv: str) -> Iterable[str]:
    """
    Get a the UV path connected by the fewest possible number of edges by
    intersecting expanding rings of UVs from either end.

    Parameters:
        start_uv: The UV at the start of the path.
        end_uv: The UV at the end of the path.
    """

    @cache
    def get_start_point_position() -> tuple[float, float]:
        return tuple(cmds.polyEditUV(start_uv, query=True))

    @cache
    def get_end_point_position() -> tuple[float, float]:
        return tuple(cmds.polyEditUV(end_uv, query=True))

    start_uv_rings: list[set[str]] = [{start_uv}]
    end_uv_rings: list[set[str]] = [{end_uv}]
    # Getting the component shape is done early
    # in order to raise an error if the UVs are not on the same shape,
    # but is also used when raising an error, and for use with the polySelect
    # command
    shape: str = get_components_shape((start_uv, end_uv))
    uvs: set[str] = {start_uv}
    expanded_uvs: set[str]
    ring_uvs: set[str]
    # Get a set of rings grown from the start UV
    while end_uv not in uvs:
        expanded_uvs = add_shared_face_edge_uvs(uvs)
        ring_uvs = expanded_uvs - uvs
        if not ring_uvs:
            # If we can't expand any further, and still haven't reached
            # the end UV, it's not a contiguous mesh
            raise NonContiguousMeshSelectionError(shape)
        start_uv_rings.append(ring_uvs)
        uvs = expanded_uvs
    uvs = {end_uv}
    # Get a set of rings grown from the end UV
    while start_uv not in uvs:
        # Stop when we've reached the start UV
        if start_uv in uvs:
            break
        expanded_uvs = add_shared_face_edge_uvs(uvs)
        ring_uvs = expanded_uvs - uvs
        end_uv_rings.append(ring_uvs)
        uvs = expanded_uvs
    # We should now have two sets of UV rings of equal length
    start_uv_ring: set[str]
    end_uv_ring: set[str]
    uv: str = ""
    for start_uv_ring, end_uv_ring in zip(
        start_uv_rings, reversed(end_uv_rings)
    ):
        ring_intersection: set[str] = start_uv_ring & end_uv_ring
        # There will typically be only one intersecting UV, however
        # when there is more than one shortest (having the least edges)
        # path between the UVs, we need to make sure that the path
        # we choose is contiguous. When multiple contiguous options for
        # traversal exist, we choose the one which is most nearly aligned
        # with the vector between the start and end UVs.
        if uv and len(ring_intersection) > 1:
            # Intersect with only the UVs adjacent to the previously
            # yielded UV
            ring_intersection &= add_shared_face_edge_uvs({uv})
        if len(ring_intersection) > 1:
            uv = get_least_deviant_midpoint_uv(
                get_start_point_position(),
                get_end_point_position(),
                ring_intersection,
            )
        else:
            uv = ring_intersection.pop()
        yield uv


def iter_shortest_vertices_path(vertices: Iterable[str]) -> Iterable[str]:
    """
    Given two or more vertices, yield the vertices forming the shortest
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
        segment_vertices: Iterable[str] = iter_shortest_vertex_path(
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


def iter_shortest_uvs_path(uvs: Iterable[str]) -> Iterable[str]:
    """
    Given two or more UVs, yield the UVs forming the shortest
    path between them.

    Parameters:
        uvs: Two or more UVs.
    """
    uvs = iter(uvs)
    try:
        start_uv: str = next(uvs)
    except StopIteration:
        return
    is_first: bool = True
    end_uv: str
    for end_uv in uvs:
        segment_uvs: Iterable[str] = iter_shortest_uv_path(
            start_uv,
            end_uv,
        )
        yield from (
            segment_uvs
            if is_first
            # Skip the first UV for segments after the first
            else islice(segment_uvs, 1, None)
        )
        start_uv = end_uv
        is_first = False


def iter_vertices_path_proportional_positions(
    vertices: Iterable[str], spans: int = 1
) -> Iterable[tuple[str, float]]:
    """
    Given two or more adjacent vertices, yield tuples with each vertex and a
    number from 0 to `spans` indicating where on the path each vertex should
    be positioned for proportional distribution.

    Parameters:
        vertices: Two or more vertices.

    Yields:
        A tuple containing the vertex name and a number from 0-`spans`
        indicating where on the curve or surface the vertex should be
        positioned.
    """
    vertices = vertices if isinstance(vertices, tuple) else tuple(vertices)
    edge_lengths: list[float] = []
    previous_vertex: str = ""
    vertex: str
    edge_length: float
    for vertex in vertices:
        if previous_vertex:
            try:
                edge: str = cmds.polyListComponentConversion(
                    previous_vertex,
                    vertex,
                    fromVertex=True,
                    toEdge=True,
                    internal=True,
                )[0]
            except IndexError as error:
                raise InvalidSelectionError(vertices) from error
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
        yield vertex, spans * (traversed_edge_length / total_edge_length)


def iter_uvs_path_proportional_positions(
    uvs: Iterable[str], spans: int = 1
) -> Iterable[tuple[str, float]]:
    """
    Given two or more adjacent UVs, yield tuples with each UV and a
    number from 0 to `spans` indicating where on the path each UV should
    be positioned for proportional distribution.

    Parameters:
        uvs: Two or more UVs.

    Yields:
        A tuple containing the UV name and a number from 0-`spans`
        indicating where on the curve or surface the UV should be
        positioned.
    """
    uvs = uvs if isinstance(uvs, tuple) else tuple(uvs)
    edge_lengths: list[float] = []
    previous_uv: str = ""
    uv: str
    edge_length: float
    for uv in uvs:
        if previous_uv:
            try:
                edge: str = get_uvs_shared_edge(previous_uv, uv)
            except IndexError as error:
                raise InvalidSelectionError(uvs) from error
            edge_length = cmds.arclen(edge)
            if not edge_length:
                raise ValueError(edge)
            edge_lengths.append(
                # The length of the preceding edge
                edge_length
            )
        else:
            edge_lengths.append(0)
        previous_uv = uv
    total_edge_length: float = sum(edge_lengths)
    traversed_edge_length: float = 0.0
    for uv, edge_length in zip(uvs, edge_lengths):
        traversed_edge_length += edge_length
        yield uv, spans * (traversed_edge_length / total_edge_length)


def iter_shortest_vertices_path_proportional_positions(
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
    selected_vertices = tuple(selected_vertices)
    yield from iter_vertices_path_proportional_positions(
        iter_shortest_vertices_path(selected_vertices),
        spans=len(selected_vertices) - 1,
    )


def iter_shortest_uvs_path_proportional_positions(
    selected_uvs: Iterable[str],
) -> Iterable[tuple[str, float]]:
    """
    Given two or more UVs, yield the UVs forming the shortest
    path between them, along with a number from 0-1 indicating where on the
    path each UV should be positioned for proportional distribution.

    Parameters:
        uvs: Two or more UVs.

    Yields:
        A tuple containing the UV name and a number from 0-1 indicating
        where on the path the UV should be positioned.
    """
    selected_uvs = tuple(selected_uvs)
    yield from iter_uvs_path_proportional_positions(
        iter_shortest_uvs_path(selected_uvs),
        spans=len(selected_uvs) - 1,
    )


def iter_vertices_path_uniform_positions(
    vertices: Iterable[str], spans: int = 1
) -> Iterable[tuple[str, float]]:
    """
    Given two or more adjacent vertices, yield each along with a number
    from 0-`spans` indicating where on the curve or surface each vertex should
    be positioned for uniform distribution.

    Parameters:
        vertices: Two or more vertices.

    Yields:
        A tuple containing the vertex name and a number from 0-`spans`
        indicating where on the curve or surface the vertex should be
        positioned.
    """
    vertices = vertices if isinstance(vertices, tuple) else tuple(vertices)
    index: int
    edge_length: int = len(vertices) - 1
    for index, vertex in enumerate(
        vertices,
    ):
        yield vertex, (index / edge_length) * spans


def iter_uvs_path_uniform_positions(
    uvs: Iterable[str], spans: int = 1
) -> Iterable[tuple[str, float]]:
    """
    Given two or more adjacent UVs, yield each along with a number
    from 0-`spans` indicating where on the curve or surface each UV should
    be positioned for uniform distribution.

    Parameters:
        uvs: Two or more UVs.

    Yields:
        A tuple containing the UV name and a number from 0-`spans`
        indicating where on the curve or surface the UV should be
        positioned.
    """
    uvs = uvs if isinstance(uvs, tuple) else tuple(uvs)
    index: int
    edge_length: int = len(uvs) - 1
    for index, uv in enumerate(
        uvs,
    ):
        yield uv, (index / edge_length) * spans


def iter_shortest_vertices_path_uniform_positions(
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
    selected_vertices = tuple(selected_vertices)
    yield from iter_vertices_path_uniform_positions(
        iter_shortest_vertices_path(selected_vertices),
        spans=len(selected_vertices) - 1,
    )


def iter_shortest_uvs_path_uniform_positions(
    selected_uvs: Iterable[str],
) -> Iterable[tuple[str, float]]:
    """
    Given two or more UVs, yield the UVs forming the shortest
    path between them, along with a number from 0-1 indicating where on the
    path each UV should be positioned for uniform distribution.

    Parameters:
        uvs: Two or more UVs.

    Yields:
        A tuple containing the UV name and a number from 0-1 indicating
        where on the path the UV should be positioned.
    """
    selected_uvs = tuple(selected_uvs)
    yield from iter_uvs_path_uniform_positions(
        iter_shortest_uvs_path(selected_uvs),
        spans=len(selected_uvs) - 1,
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


def _get_rotated_uv_loop(
    uvs: tuple[str, ...], terminal_uv: str
) -> tuple[str, ...]:
    """
    Rotate a (closed) UV loop so the `terminal_uv` is the first
    and last UV in the loop.
    """
    # This logic is identical for UVs and vertices, so we can reuse it
    return _get_rotated_vertex_loop(uvs, terminal_uv)


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
    for vertex_loop in vertex_loops[1:]:
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


def _iter_directionally_aligned_uv_loops(
    uv_loops: Sequence[tuple[str, ...]],
) -> Iterable[tuple[str, ...]]:
    """
    Given a series of UV loops, reverse where needed to make them all
    sorted in the same direction
    """
    reference_uv: str = uv_loops[0][1]
    yield uv_loops[0]
    uv_loop: tuple[str, ...]
    for uv_loop in uv_loops:
        penterminus_uvs: tuple[str, str] = (
            uv_loop[1],
            uv_loop[-2],
        )
        if (
            tuple(
                iter_sort_uvs_by_distance(reference_uv, set(penterminus_uvs))
            )
            == penterminus_uvs
        ):
            yield uv_loop
        else:
            # Since the next-to-last UV was closed than the second
            # UV to the reference, we need to reverse the loop
            yield tuple(reversed(uv_loop))


def _iter_align_closed_loop_contiguous_edges(
    edge_loops: list[tuple[str, ...]],
) -> Iterable[tuple[str, ...]]:
    """
    This function yields sorted and aligned rearrangements of the (closed)
    edge loops provided as input.
    """
    if len(edge_loops) == 1:
        yield from edge_loops
        return
    edge_loop: tuple[str, ...]
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


def _iter_align_closed_loop_contiguous_uvs(
    uv_loops: list[tuple[str, ...]],
) -> Iterable[tuple[str, ...]]:
    """
    This function yields sorted and aligned rearrangements of the (closed)
    UV loops provided as input.
    """
    if len(uv_loops) == 1:
        yield from uv_loops
        return
    # Find a corner UV by getting the furthest UV from the first start
    # UV
    other_uvs: set[str] = set()
    uv_loop: tuple[str, ...]
    for uv_loop in uv_loops[1:]:
        other_uvs |= set(uv_loop)
    # Finding the UV the furthest from any in one of our loops would work,
    # but we can marginaslly reduce overhead by use a known endpoint and
    # excluding the UVs in that end points looop
    origin_uv: str = find_end_uv(other_uvs, origin_uv=uv_loops[0][0])
    uv_loop_sets: tuple[set[str], ...] = tuple(map(set, uv_loops))
    unused_loop_indices: set[int] = set(range(len(uv_loops)))
    # Now we will find the closest UV to the origin on each other loop,
    # and align the UV loops so that each begins/ends with that UV
    uvs: set[str] = {origin_uv}
    sorted_uv_loops: list[tuple[str, ...]] = []
    while unused_loop_indices:
        index: int
        for index in tuple(unused_loop_indices):
            matched_uvs: set[str] = uvs & uv_loop_sets[index]
            if matched_uvs:
                sorted_uv_loops.append(
                    _get_rotated_uv_loop(uv_loops[index], matched_uvs.pop())
                )
                unused_loop_indices.remove(index)
                break
        if unused_loop_indices:
            shared_edge_uvs: set = get_shared_face_edge_uvs(uvs)
            if not shared_edge_uvs:
                # If there are loops unconsumed, but we can't grow the
                # UV selection any further, the mesh is likely not
                # contiguous
                raise NonContiguousMeshSelectionError(uv_loops)
            uvs |= shared_edge_uvs
    for uv_loop in _iter_directionally_aligned_uv_loops(sorted_uv_loops):
        yield uv_loop


def is_closed_edge_loop(edges: tuple[str, ...]) -> bool:
    """
    Given a tuple of (sorted) edges, return `True` if they form
    a closed loop, otherwise return `False`
    """
    return bool(
        set(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    edges[0],
                    toVertex=True,
                    fromEdge=True,
                ),
                flatten=True,
            )
        )
        & set(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    edges[-1],
                    toVertex=True,
                    fromEdge=True,
                ),
                flatten=True,
            )
        )
    )


def iter_aligned_contiguous_edges(  # noqa: C901
    *selected_edges: str,
) -> Iterable[tuple[str, ...]]:
    """
    Given one or more groups of aligned contiguous edges, yield a tuple
    containing each set of contiguous edges
    """
    edge_loop_segments: list[tuple[str, ...]] = list(
        iter_contiguous_edges(*selected_edges)
    )
    if (
        len(edge_loop_segments[0]) > 2  # noqa: PLR2004
        and edge_loop_segments[0][0] != edge_loop_segments[0][-1]
        and is_closed_edge_loop(edge_loop_segments[0])
    ):
        # If the first and last edges share a vertex, the edges form a closed
        # loop, so we require an alternate alignment strategy
        yield from _iter_align_closed_loop_contiguous_edges(edge_loop_segments)
        return
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
    # Since it's now unused, we will re-populate `edge_loop_segments`
    # with sorted edge loops
    edge_loop_segments.clear()
    edge_loop_ids: list[set[int]] = []
    # Sort the edge loops
    start_vertex: str
    for start_vertex in iter_sorted_vertices(start_vertices_edges.keys()):
        edge_loop_segment: tuple[str, ...] = start_vertices_edges[start_vertex]
        edge_loop_segments.append(edge_loop_segment)
        edge_loop_ids.append(set(map(get_component_id, edge_loop_segment)))
    # Trim edges which don't have a corresponding edge (one on the same ring)
    # on all other segments
    shape: str = get_components_shape(chain(*edge_loop_segments))
    length: int = len(edge_loop_segments)
    for index, edge_loop_segment in enumerate(edge_loop_segments):
        start_index: int = 0
        stop_index: int | None = None
        segment_length: int = len(edge_loop_segment)
        segment_index: int
        edge: str
        ring_edge_ids: set[int]
        matched: bool
        other_index: int
        for segment_index, edge in enumerate(edge_loop_segment):
            ring_edge_ids = set(
                cmds.polySelect(shape, edgeRing=get_component_id(edge))
            )
            matched = True
            for other_index in range(length):
                if other_index == index:
                    continue
                if not ring_edge_ids & edge_loop_ids[other_index]:
                    matched = False
                    break
            if matched:
                start_index = segment_index
                break
        for segment_index, edge in enumerate(reversed(edge_loop_segment)):
            ring_edge_ids = set(
                cmds.polySelect(shape, edgeRing=get_component_id(edge))
            )
            matched = True
            for other_index in range(length):
                if other_index == index:
                    continue
                if not ring_edge_ids & edge_loop_ids[other_index]:
                    matched = False
                    break
            if matched:
                stop_index = segment_length - segment_index
                break
        yield edge_loop_segment[start_index:stop_index]


def iter_aligned_contiguous_uvs(
    *selected_uvs: str,
) -> Iterable[tuple[str, ...]]:
    """
    Given one or more groups of UVs which are contiguous in the UV space,
    yield a tuple containing each set of contiguous UVs,
    directionally aligned. If one of the contiguous UV sets is not on the
    same mesh as the rest, it will be discarded/ignored.
    """
    uv_loop_segments: list[tuple[str, ...]] = list(
        iter_contiguous_uvs(*selected_uvs)
    )
    if (
        len(uv_loop_segments[0]) > 2  # noqa: PLR2004
        and uv_loop_segments[0][0] != uv_loop_segments[0][-1]
        and (
            # Check to see if the end UVs are adjacent
            uv_loop_segments[0][-1]
            in get_shared_face_edge_uvs({uv_loop_segments[0][0]})
        )
    ):
        # If UVs form a closed loop, we require an alternate alignment
        # strategy
        yield from _iter_align_closed_loop_contiguous_uvs(uv_loop_segments)
        return
    # Get the start and end uvs for each segment
    uv_loop_segment: tuple[str, ...]
    origin_uv: str | None = None
    segment_terminal_uvs: tuple[str, ...]
    start_uvs_loops: dict[str, tuple[str, ...]] = {}
    for index, segment_terminal_uvs in enumerate(
        (uv_loop_segment[0], uv_loop_segment[-1])
        for uv_loop_segment in uv_loop_segments
    ):
        if origin_uv is None:
            start_uvs_loops[segment_terminal_uvs[0]] = tuple(
                uv_loop_segments[index]
            )
            # This uv will be used to align subsequent segments
            origin_uv = segment_terminal_uvs[0]
        else:
            sorted_segment_terminal_uvs: tuple[str, ...] = tuple(
                iter_sort_uvs_by_distance(origin_uv, set(segment_terminal_uvs))
            )
            start_uvs_loops[sorted_segment_terminal_uvs[0]] = tuple(
                uv_loop_segments[index]
                if (sorted_segment_terminal_uvs == segment_terminal_uvs)
                # If the terminal uvs changed order when sorted, the
                # segment was inverted, so we reverse it
                else reversed(uv_loop_segments[index])
            )
    # Sort the UV loops
    # We re-use `uv_loop_segments` as it's no longer being used
    start_uv: str
    uv_loop_segments = [
        start_uvs_loops[start_uv]
        for start_uv in iter_sorted_uvs(start_uvs_loops.keys())
    ]
    # Not we remove end UVs which are further from other segment
    # ends than another UV in the segment (overhanging segment parts)
    for index, uv_loop_segment in enumerate(uv_loop_segments):
        start_index: int = 0
        stop_index: int = len(uv_loop_segment)
        uv_loop_segment_set: set[str] = set(uv_loop_segment)
        other_index: int
        other_uv_loop_segment: tuple[str, ...]
        for other_index, other_uv_loop_segment in enumerate(uv_loop_segments):
            if other_index == index:
                continue
            # If there is a UV closer to the other segment's first UV
            # than the first UV in this segment, we move the start of this
            # segment to that UV
            start_index = max(
                start_index,
                uv_loop_segment.index(
                    next(
                        iter(
                            iter_sort_uvs_by_distance(
                                other_uv_loop_segment[0], uv_loop_segment_set
                            )
                        )
                    )
                ),
            )
            # If there is a UV closer to the other segment's last UV
            # than the last UV in this segment, we move the end of this segment
            # to that UV
            stop_index = min(
                stop_index,
                uv_loop_segment.index(
                    next(
                        iter(
                            iter_sort_uvs_by_distance(
                                other_uv_loop_segment[-1], uv_loop_segment_set
                            )
                        )
                    )
                )
                + 1,
            )
        yield uv_loop_segment[start_index:stop_index]


def iter_contiguous_edges(  # noqa: C901
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
    yield from map(tuple, filter(None, edge_loop_segments))


def iter_contiguous_uv_edges(  # noqa: C901
    *selected_edges: str,
) -> Iterable[tuple[str, ...]]:
    """
    Yield tuples of edge loop segments which are contiguous in the UV space.

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
        adjacent_edges: set[str] = set(get_shared_uv_edges({edge}))
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
    yield from map(tuple, filter(None, edge_loop_segments))


def iter_contiguous_uvs(  # noqa: C901
    *selected_uvs: str,
) -> Iterable[tuple[str, ...]]:
    """
    Yield tuples of UV loop segment, each of which are contiguous, and all
    of which reside on the same UV shell.

    Parameters:
        selected_uvs: Two or more UV loop segments comprised of equal
            numbers of UVs each, with ends alignged along perpendicular
            edge loops forming a rectangular section of a UV mesh.
    """
    uvs: set[str] = set(selected_uvs)
    uv_loop_segments: list[list[str]] = []
    uv_loop_segment: list[str]
    # This list stores one UV ID per/loop, in order to subsequently determine
    # if any don't share a UV shell
    representative_uv_ids: list[int | None] = []
    # Organize edges into contiguous segments
    while uvs:
        uv: str = uvs.pop()
        adjacent_uvs: set[str] = get_shared_face_edge_uvs({uv})
        # This is a list of UV loop segment indices where the UV could be
        # appended. Since two segments could be matched for the same UV,
        # we need to retain this as a list.
        found: int | None = None
        index: int
        for index, uv_loop_segment in enumerate(uv_loop_segments):
            if not uv_loop_segment:
                continue
            if uv_loop_segment[0] in adjacent_uvs:
                # This edge is adjacent to the first edge in the segment
                if found is None:
                    uv_loop_segment.insert(0, uv)
                    found = index
                    # Keep looking to see if there is a second match
                    continue
                else:
                    if uv == uv_loop_segments[found][-1]:
                        uv_loop_segments[found].extend(uv_loop_segment)
                    else:
                        uv_loop_segments[found] = (
                            list(reversed(uv_loop_segment))
                            + uv_loop_segments[found]
                        )
                    uv_loop_segment.clear()
                    representative_uv_ids[index] = None
                    break
            if uv_loop_segment[-1] in adjacent_uvs:
                # This UV is adjacent to the last UV in the segment
                if found is None:
                    uv_loop_segment.append(uv)
                    found = index
                    # Keep looking to see if there is a second match
                    continue
                else:
                    if uv == uv_loop_segments[found][-1]:
                        uv_loop_segments[found].extend(
                            reversed(uv_loop_segment)
                        )
                    else:
                        uv_loop_segments[found] = (
                            list(uv_loop_segment) + uv_loop_segments[found]
                        )
                    uv_loop_segment.clear()
                    representative_uv_ids[index] = None
                    break
        if found is None:
            # This UV is not adjacent to any segments started thus far
            uv_loop_segments.append([uv])
            representative_uv_ids.append(get_component_id(uv))
    # If there are more than 2 UV loop segments, check to see if one is an
    # orphan, and abandon any orphans
    if len(uv_loop_segments) > 2:  # noqa: PLR2004
        shape: str = get_components_shape(selected_uvs)
        # Clear UV loops which aren't on the same shell as the rest
        uv_id: int | None
        other_index: int
        other_uv_id: int | None
        for index, uv_id in enumerate(representative_uv_ids):
            if uv_id is None:
                continue
            found_path: bool = False
            for other_index, other_uv_id in enumerate(representative_uv_ids):
                if other_uv_id is None:
                    continue
                if index == other_index:
                    continue
                if cmds.polySelect(
                    shape, shortestEdgePathUV=(uv_id, other_uv_id), query=True
                ):
                    found_path = True
                    break
            if not found_path:
                uv_loop_segments[index].clear()
    # Remove the cleared segments (they've been joined with another)
    yield from map(tuple, filter(None, uv_loop_segments))


def get_polymesh_shape_uvs_positions(
    shape: str,
) -> dict[int, tuple[float, float]]:
    """
    Intended for testing, this function returns a mapping of UV IDs
    to the UV-space coordinates
    """
    uvs_positions: dict[int, tuple[float, float]] = {}
    uv: str
    for uv in cmds.ls(f"{shape}.map[*]", flatten=True):
        uvs_positions[get_component_id(uv)] = tuple(
            cmds.polyEditUV(uv, query=True)
        )
    return uvs_positions


def get_polymesh_shape_vertices_positions(
    shape: str,
) -> dict[int, tuple[float, float, float]]:
    """
    Intended for testing, this function returns a mapping of vertex IDs
    to their 3d translation coordinates
    """
    vertices_positions: dict[int, tuple[float, float, float]] = {}
    vertex: str
    for vertex in cmds.ls(f"{shape}.vtx[*]", flatten=True):
        vertices_positions[get_component_id(vertex)] = tuple(
            cmds.pointPosition(vertex)
        )
    return vertices_positions


def get_polymesh_shape_changed_vertices_positions(
    shape: str, vertices_positions: dict[int, tuple[float, float, float]]
) -> dict[int, tuple[float, float, float]]:
    """
    Intended for testing, this function returns a mapping of vertex IDs
    to their 3d translation coordinates for vertices which differ
    from those in the input `vertices_positions`.
    """
    changed_vertices_positions: dict[int, tuple[float, float, float]] = {}
    vertex: str
    for vertex in cmds.ls(f"{shape}.vtx[*]", flatten=True):
        vertex_id: int = get_component_id(vertex)
        point_position: tuple[float, float, float] = tuple(
            cmds.pointPosition(vertex)
        )
        if point_position != vertices_positions.get(vertex_id):
            changed_vertices_positions[vertex_id] = point_position
    return changed_vertices_positions


def get_polymesh_shape_changed_uvs_positions(
    shape: str, uvs_positions: dict[int, tuple[float, float]]
) -> dict[int, tuple[float, float]]:
    """
    Intended for testing, this function returns a mapping of UV IDs
    to their UV space coordinates for UVs which differ
    from those in the input `uvs_positions`.
    """
    changed_uvs_positions: dict[int, tuple[float, float]] = {}
    uv: str
    for uv in cmds.ls(f"{shape}.map[*]", flatten=True):
        uv_id: int = get_component_id(uv)
        point_position: tuple[float, float] = tuple(
            cmds.polyEditUV(uv, query=True)
        )
        if point_position != uvs_positions.get(uv_id):
            changed_uvs_positions[uv_id] = point_position
    return changed_uvs_positions
