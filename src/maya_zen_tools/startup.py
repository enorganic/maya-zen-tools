"""
This module is designed to be imported at Maya startup, and should be added
to your userSetup.py script by running `mayapy -m maya_zen_tools.install`.
"""

from __future__ import annotations

import contextlib

from maya import cmds  # type: ignore

from maya_zen_tools.menu import create_menu
from maya_zen_tools.upgrade import upgrade


def set_selection_priority() -> None:
    """
    This sets selection priority needed for manipulating deformers effectively
    """
    surface_selection_priority: int = (
        cmds.selectPriority(
            query=True,
            nurbsSurface=True,
        )
        or 0
    )
    curve_selection_priority: int = (
        cmds.selectPriority(
            query=True,
            nurbsCurve=True,
        )
        or 0
    )
    polymesh_selection_priority: int = (
        cmds.selectPriority(
            query=True,
            polymesh=True,
        )
        or 0
    )
    locator_selection_priority: int = (
        cmds.selectPriority(
            query=True,
            locatorXYZ=True,
        )
        or 0
    )
    # Surface selection should be higher priority than polymesh selection
    if surface_selection_priority <= polymesh_selection_priority:
        surface_selection_priority = polymesh_selection_priority + 1
        cmds.selectPriority(
            nurbsSurface=surface_selection_priority,
        )
    # Curve selection should be higher priority than surface selection
    if curve_selection_priority <= surface_selection_priority:
        curve_selection_priority = surface_selection_priority + 1
        cmds.selectPriority(
            nurbsCurve=curve_selection_priority,
        )
    # Locator selection priority should be higher than curve selection
    if locator_selection_priority <= curve_selection_priority:
        locator_selection_priority = curve_selection_priority + 1
        cmds.selectPriority(
            locatorXYZ=locator_selection_priority,
        )


def main() -> None:
    """
    The main entry point for `maya-zen-tools startup`.
    """
    # Don't raise errors if the upgrade fails, just continue to use the
    # installed version
    with contextlib.suppress(Exception):
        upgrade()
    # Set selection preferences to track selection order
    cmds.selectPref(
        trackSelectionOrder=True,
    )
    set_selection_priority()
    create_menu()


cmds.evalDeferred(main)
