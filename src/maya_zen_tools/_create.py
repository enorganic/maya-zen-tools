from __future__ import annotations

from typing import Iterable

from maya import cmds  # type: ignore

from maya_zen_tools._traverse import (
    get_component_id,
    get_components_shape,
    get_transform_shape,
    iter_edges_uvs,
    iter_edges_vertices,
)


def create_locator(
    *,
    translate: tuple[float, float, float] | None = None,
    scale: float = 1.0,
    connect_translate: str | tuple[str] | None = None,
    parent: str = "",
) -> str:
    """
    Create a locator at the given translation.

    Parameters:
        translation: The translation of the locator.
        scale: The scale of the locator.
    """
    locator: str = cmds.spaceLocator(name="wireLocator#")[0]
    cmds.setAttr(f"{locator}.translate", *translate)
    locator_shape: str = cmds.listRelatives(
        locator, shapes=True, noIntermediate=True
    )[0]
    cmds.setAttr(f"{locator_shape}.localScale", scale, scale, scale)
    if connect_translate is not None:
        if isinstance(connect_translate, str):
            connect_translate = (connect_translate,)
        connect_translate_to: str
        for connect_translate_to in connect_translate:
            cmds.connectAttr(
                f"{locator}.translate",
                connect_translate_to,
            )
    if parent:
        cmds.parent(locator, parent)
    return locator


def create_edges_rebuild_curve(edges: Iterable[str]) -> str:
    """
    Create a rebuildCurve node from contiguous edges
    """
    edges = tuple(edges)
    vertices: tuple[str, ...] = tuple(iter_edges_vertices(edges))
    polymesh_shape: str = get_components_shape(edges)
    point_on_curve_info: str = cmds.createNode("pointOnCurveInfo")
    cmds.setAttr(f"{point_on_curve_info}.parameter", 0)
    cmds.setAttr(f"{point_on_curve_info}.turnOnPercentage", 1)
    edge: str
    curve_from_mesh_edges: str = ""
    vertex: str
    reverse_previous: bool = True
    reverse: bool = False
    for vertex, edge in zip(vertices[:-1], edges):
        curve_from_mesh_edge: str = cmds.createNode("curveFromMeshEdge")
        cmds.connectAttr(
            f"{polymesh_shape}.worldMesh[0]",
            f"{curve_from_mesh_edge}.inputMesh",
        )
        cmds.setAttr(
            f"{curve_from_mesh_edge}.edgeIndex[0]", get_component_id(edge)
        )
        cmds.connectAttr(
            f"{curve_from_mesh_edge}.outputCurve",
            f"{point_on_curve_info}.inputCurve",
            # Force the connection (replace the pre-existing connection)
            force=True,
        )
        # Determine if we need to reverse the curve
        vertex_point_position: tuple[float, float, float] = tuple(
            cmds.pointPosition(vertex)
        )
        curve_start_point_position: tuple[float, float, float] = cmds.getAttr(
            f"{point_on_curve_info}.position"
        )[0]
        reverse = vertex_point_position != curve_start_point_position
        if not curve_from_mesh_edges:
            # This is the first curve, no need to attach anything
            curve_from_mesh_edges = curve_from_mesh_edge
            # There was no attach node in this iteration, so we carry
            # over reversal to the next iteration
            reverse_previous = reverse
            continue
        # Attach the edge curve to the pre-existing curve
        attach_curve: str = cmds.createNode("attachCurve")
        # Set the attach curve node state to "waiting"
        cmds.setAttr(f"{attach_curve}.nodeState", 8)
        cmds.connectAttr(
            f"{curve_from_mesh_edges}.outputCurve",
            f"{attach_curve}.inputCurve1",
        )
        cmds.connectAttr(
            f"{curve_from_mesh_edge}.outputCurve",
            f"{attach_curve}.inputCurve2",
        )
        # Set the attach curve node state to "active"
        cmds.setAttr(f"{attach_curve}.nodeState", 0)
        # Reverse the curve and/or previous curve so that the start of the
        # curve aligns with `vertex`
        if reverse_previous:
            cmds.setAttr(f"{attach_curve}.reverse1", 1)
        if reverse:
            cmds.setAttr(f"{attach_curve}.reverse2", 1)
        reverse_previous = False
        curve_from_mesh_edges = attach_curve
    rebuild_curve: str = cmds.createNode("rebuildCurve")
    cmds.connectAttr(
        f"{curve_from_mesh_edges}.outputCurve", f"{rebuild_curve}.inputCurve"
    )
    cmds.setAttr(f"{rebuild_curve}.keepControlPoints", 1)
    cmds.setAttr(f"{rebuild_curve}.degree", 1)
    cmds.setAttr(f"{rebuild_curve}.rebuildType", 0)
    cmds.setAttr(f"{rebuild_curve}.spans", len(edges))
    cmds.setAttr(f"{rebuild_curve}.endKnots", 1)
    # Make the range 0 -> # spans
    cmds.setAttr(f"{rebuild_curve}.keepRange", 2)
    return rebuild_curve


def create_uv_edges_rebuild_curve(
    edges: Iterable[str],
) -> tuple[str, str, str]:
    """
    Create a (rebuilt) curve in UV space from contiguous edges
    """
    return create_uvs_rebuild_curve(iter_edges_uvs(edges))


def create_uvs_rebuild_curve(
    uvs: Iterable[str],
) -> tuple[str, str, str]:
    """
    Create a (rebuilt) curve in UV space from contiguous edges
    """
    uvs = tuple(uvs)
    curve_transform: str = cmds.curve(
        editPoint=tuple((*cmds.polyEditUV(uv, query=True), 0.0) for uv in uvs),
        degree=1,
    )
    curve_shape: str = get_transform_shape(curve_transform)
    rebuild_curve: str = cmds.createNode("rebuildCurve")
    cmds.connectAttr(f"{curve_shape}.local", f"{rebuild_curve}.inputCurve")
    cmds.setAttr(f"{rebuild_curve}.keepControlPoints", 1)
    cmds.setAttr(f"{rebuild_curve}.degree", 1)
    cmds.setAttr(f"{rebuild_curve}.rebuildType", 0)
    cmds.setAttr(f"{rebuild_curve}.spans", len(uvs) - 1)
    cmds.setAttr(f"{rebuild_curve}.endKnots", 1)
    # Make the range 0 -> # spans
    cmds.setAttr(f"{rebuild_curve}.keepRange", 2)
    return rebuild_curve, curve_shape, curve_transform
