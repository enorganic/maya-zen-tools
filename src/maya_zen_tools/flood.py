from __future__ import annotations

from typing import Iterable

from maya import cmds  # type: ignore

from maya_zen_tools._traverse import (
    get_components_shape,
)


def _iter_flood_select_vertices(
    selected_vertices: tuple[str, ...], selected_edges: tuple[str, ...]
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


def _iter_flood_select_faces(
    selected_faces: tuple[str, ...], selected_edges: tuple[str, ...]
) -> Iterable[str]:
    if not selected_faces:
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
    vertices: set[str] = set(
        cmds.ls(
            *cmds.polyListComponentConversion(
                *selected_faces,
                fromFace=True,
                toVertex=True,
            ),
            flatten=True,
        )
    )


def _iter_flood_select_uvs(
    selected_uvs: tuple[str, ...], selected_edges: tuple[str, ...]
) -> Iterable[str]:
    if not selected_uvs:
        return
    border_uvs: set[str] = (
        set(
            cmds.ls(
                *cmds.polyListComponentConversion(
                    *selected_edges, fromEdge=True, toUV=True
                ),
                flatten=True,
            )
        )
        if selected_edges
        else set()
    )


def flood_select(*selection: str) -> tuple[str, ...]:
    """
    Given a selection comprised of one or more polymesh faces, vertices, or
    UVs, and a set of edges enclosing an area around the faces, vertices, or
    UVs—select all faces or vertices within the enclosed area.
    """
    cmds.waitCursor(state=True)
    selection: tuple[str, ...] = tuple(selection or cmds.ls(selection=True))
    selected_faces: tuple[str, ...] = tuple(
        cmds.polyListComponentConversion(
            *selection, fromFace=True, toFace=True
        )
    )
    selected_vertices: tuple[str, ...] = tuple(
        cmds.polyListComponentConversion(
            *selection, fromVertex=True, toVertex=True
        )
    )
    selected_uvs: tuple[str, ...] = tuple(
        cmds.polyListComponentConversion(*selection, fromUV=True, toUV=True)
    )
    selected_edges: tuple[str, ...] = tuple(
        cmds.polyListComponentConversion(
            *selection, fromEdge=True, toEdge=True
        )
    )
    # Raise an error if selected vertices span more than one mesh
    get_components_shape(selected_faces + selected_vertices + selected_uvs)
    selected_components: tuple[str, ...] = (
        tuple(_iter_flood_select_vertices(selected_vertices, selected_edges))
        + tuple(_iter_flood_select_uvs(selected_uvs, selected_edges))
        + tuple(_iter_flood_select_faces(selected_faces, selected_edges))
    )
    # Grow the selection until
    cmds.waitCursor(state=False)
    return selected_components
