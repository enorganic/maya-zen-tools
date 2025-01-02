from __future__ import annotations

from datetime import datetime, timezone

from maya import cmds  # type: ignore

from maya_zen_tools._utilities import (
    get_maya_zen_tools_package_info,  # type: ignore
)

# UI Components
MAYA_WINDOW: str = "MayaWindow"
MENU_SET: str = "modelingMenuSet"
MENU: str = "zenToolsMenu"

# Labels
SELECT_EDGES_BETWEEN_VERTICES_LABEL: str = "Select Edges Between Vertices"
FLOOD_SELECT_LABEL: str = "Flood Select"
CURVE_DISTRIBUTE_BETWEEN_VERTICES_LABEL: str = (
    "Curve Distribute Between Vertices"
)
LOFT_DISTRIBUTE_BETWEEN_EDGE_LOOPS_LABEL: str = (
    "Loft Distribute Between Edge Loops"
)
ABOUT_WINDOW: str = "zenToolsAboutWindow"


def show_about() -> None:
    """
    Show a window with information about, and button to update/upgrade or
    uninstall, ZenTools.
    """
    if cmds.window(ABOUT_WINDOW, exists=True):
        cmds.deleteUI(ABOUT_WINDOW)
    cmds.window(
        ABOUT_WINDOW,
        title="About ZenTools",
    )
    column_layout: str = cmds.columnLayout(
        parent=ABOUT_WINDOW,
        margins=15,
    )
    version: str = get_maya_zen_tools_package_info()["version"]
    cmds.text(
        label=(
            f"ZenTools {version} © "
            f"{datetime.now(tz=timezone.utc).year} by David Belais\n"
        ),
        align="left",
        parent=column_layout,
    )
    row_layout: str = cmds.rowLayout(
        parent=column_layout,
        numberOfColumns=2,
    )
    cmds.button(
        label="Update ZenTools",
        parent=row_layout,
        command=(
            "from maya import cmds\n"
            "from maya_zen_tools import upgrade\nupgrade.main()\n"
            f"cmds.deleteUI('{ABOUT_WINDOW}')"
        ),
    )
    cmds.button(
        label="Uninstall ZenTools",
        command=(
            "from maya import cmds\n"
            "from maya_zen_tools import _ui\n"
            "_ui.show_confirmation_dialogue("
            f'"Are you certain you want to uninstall ZenTools?", '
            f'yes_command="from maya_zen_tools import uninstall\\n'
            'uninstall.main()", title="Uninstall ZenTools?")\n'
            f"cmds.deleteUI('{ABOUT_WINDOW}')"
        ),
    )
    cmds.showWindow(ABOUT_WINDOW)


def create_menu() -> None:
    """
    Create the main ZenTools menu
    """
    if cmds.menu(MENU, exists=True):
        cmds.deleteUI(MENU)
    cmds.menu(
        MENU, label="ZenTools", tearOff=True, visible=True, parent=MAYA_WINDOW
    )
    cmds.menuSet(MENU_SET, addMenu=MENU)
    # Selection
    cmds.menuItem(
        label=SELECT_EDGES_BETWEEN_VERTICES_LABEL,
        command=(
            "from maya_zen_tools import loop\n"
            "loop.do_select_edges_between_vertices()"
        ),
        annotation=(
            "Selects an edge path containing the fewest edges necessary to "
            "connect selected vertices."
        ),
        parent=MENU,
    )
    cmds.menuItem(
        optionBox=True,
        command=(
            "from maya_zen_tools import loop\n"
            "loop.show_select_edges_between_vertices_options()"
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label="Flood Select",
        command=("from maya_zen_tools import select;select.flood_select()"),
        annotation=(
            "Selected Edges will define a selection border, selected vertices "
            "or faces will determine the portion of the mesh to be selected."
        ),
        parent=MENU,
    )
    # Mesh Tools
    cmds.menuItem(
        label=CURVE_DISTRIBUTE_BETWEEN_VERTICES_LABEL,
        command=(
            "from maya_zen_tools import loop\n"
            "loop.do_curve_distribute_vertices()"
        ),
        annotation="Align edge loop along a curve based on vertex selection.",
        parent=MENU,
    )
    cmds.menuItem(
        optionBox=True,
        command=(
            "from maya_zen_tools import loop\n"
            "loop.show_curve_distribute_vertices_options()"
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label=LOFT_DISTRIBUTE_BETWEEN_EDGE_LOOPS_LABEL,
        command=(
            "from maya_zen_tools import loft\n"
            "loft.do_loft_distribute_between_edges()"
        ),
        annotation=(
            "Distribute vertices between two or more parallel edge loops."
        ),
        parent=MENU,
    )
    cmds.menuItem(
        optionBox=True,
        command=(
            "from maya_zen_tools import loft;"
            "loft.show_loft_distribute_between_edges_options()"
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label="About ZenTools",
        command=(
            "import maya_zen_tools.menu\n" "maya_zen_tools.menu.show_about()"
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label="ZenTools Help",
        command=(
            "import webbrowser\n"
            "webbrowser.open('https://maya-zen-tools.enorganic.org')"
        ),
        parent=MENU,
    )
