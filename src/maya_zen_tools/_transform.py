from __future__ import annotations

from maya import cmds  # type: ignore


def center_pivot(
    transform: str,
) -> tuple[float, float, float]:
    center: tuple[float, float, float] = tuple(cmds.objectCenter(transform))
    cmds.setAttr(f"{transform}.rotatePivot", *center)
    cmds.setAttr(f"{transform}.scalePivot", *center)
    return center
