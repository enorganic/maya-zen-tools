from __future__ import annotations

from typing import Iterable

from maya import cmds  # type: ignore

from maya_zen_tools._traverse import (
    add_shared_face_edge_uvs,
    get_components_shape,
    get_shared_edge_vertices,
    iter_selected_components,
)
from maya_zen_tools._ui import set_wait_cursor_state


def _iter_flood_select_vertices(
    selected_vertices: Iterable[str], selected_edges: Iterable[str]
) -> Iterable[str]:
    if not selected_vertices:
        return
    border_vertices: set[str] = (
        set(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    *selected_edges, fromEdge=True, toVertex=True
                ),
                flatten=True,
            )
        )
        if selected_edges
        else set()
    )
    vertices: set[str] = set(selected_vertices)
    add_vertices: set[str] = set(selected_vertices)
    # Expand the vertex selection until no new vertices are added
    while add_vertices:
        yield from add_vertices
        # By removing border vertices, we ensure that our traversal will stop
        # at the border, and once everything inside the border has been
        # added/yielded, `add_vertices` will be empty, thereby halting the
        # loop
        add_vertices = get_shared_edge_vertices(vertices) - border_vertices
        vertices |= add_vertices
    yield from border_vertices


def _iter_flood_select_faces(
    selected_faces: Iterable[str], selected_edges: Iterable[str]
) -> Iterable[str]:
    if not selected_faces:
        return
    yield from set(
        cmds.ls(
            *cmds.polyListComponentConversion(
                *_iter_flood_select_vertices(
                    set(
                        cmds.ls(
                            *cmds.polyListComponentConversion(
                                *selected_faces,
                                fromFace=True,
                                toVertex=True,
                            ),
                            flatten=True,
                        )
                    ),
                    selected_edges,
                ),
                fromVertex=True,
                toFace=True,
                internal=True,
            ),
            flatten=True,
        )
    )


def _iter_flood_select_uvs(
    selected_uvs: Iterable[str], selected_edges: Iterable[str]
) -> Iterable[str]:
    if not selected_uvs:
        return
    border_uvs: set[str] = (
        set(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    *selected_edges, fromEdge=True, toVertex=True
                ),
                flatten=True,
            )
        )
        if selected_edges
        else set()
    )
    uvs: set[str] = set(selected_uvs)
    add_uvs: set[str] = set(selected_uvs)
    # Expand the vertex selection until no new uvs are added
    while add_uvs:
        yield from add_uvs
        # By removing border uvs, we ensure that our traversal will stop
        # at the border, and once everything inside the border has been
        # added/yielded, `add_uvs` will be empty, thereby halting the
        # loop
        add_uvs = add_shared_face_edge_uvs(uvs) - border_uvs
        uvs |= add_uvs
    yield from border_uvs


def flood_select(*selection: str) -> tuple[str, ...]:
    """
    Given a `selection` comprised of:

    - One or more polymesh faces, vertices, or UVs, and...
    - A set of edges enclosing an area around the faces, vertices, or
      UVs

    ...this function will expand the face, vertex, or UV selection to
    encompass the area enclosed by the selected edges.
    """
    set_wait_cursor_state(True)
    try:
        selection = selection or tuple(cmds.ls(selection=True, flatten=True))
        selected_faces: tuple[str, ...] = tuple(
            iter_selected_components("f", selection=selection)
        )
        selected_vertices: tuple[str, ...] = tuple(
            iter_selected_components("vtx", selection=selection)
        )
        selected_uvs: tuple[str, ...] = tuple(
            iter_selected_components("map", selection=selection)
        )
        selected_edges: tuple[str, ...] = tuple(
            iter_selected_components("e", selection=selection)
        )
        # Raise an error if selected vertices span more than one mesh
        get_components_shape(selected_faces + selected_vertices + selected_uvs)
        selected_components: tuple[str, ...] = (
            tuple(
                _iter_flood_select_vertices(selected_vertices, selected_edges)
            )
            + tuple(_iter_flood_select_uvs(selected_uvs, selected_edges))
            + tuple(_iter_flood_select_faces(selected_faces, selected_edges))
        )
        cmds.select(
            *selection,
            deselect=True,
        )
        cmds.select(*selected_components, add=True)
    finally:
        set_wait_cursor_state(False)
    return selected_components
