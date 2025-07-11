from __future__ import annotations

import contextlib
from datetime import datetime, timezone

from maya import cmds  # type: ignore

from maya_zen_tools._utilities import (
    get_maya_zen_tools_package_info,  # type: ignore
)
from maya_zen_tools.options import get_tool_option

# UI Components
MAYA_WINDOW: str = "MayaWindow"
MENU_SET: str = "modelingMenuSet"
MENU: str = "zenToolsMenu"

# Labels
SELECT_EDGES_BETWEEN_VERTICES_LABEL: str = "Select Edges Between Vertices"
SELECT_EDGES_BETWEEN_UVS_LABEL: str = "Select Edges Between UVs"
SELECT_UVS_BETWEEN_UVS_LABEL: str = "Select UVs Between UVs"
FLOOD_SELECT_LABEL: str = "Flood Select"
CURVE_DISTRIBUTE_BETWEEN_VERTICES_LABEL: str = (
    "Curve Distribute Between Vertices"
)
LOFT_DISTRIBUTE_VERTICES_BETWEEN_EDGES_LABEL: str = (
    "Loft Distribute Vertices Between Edges"
)
CURVE_DISTRIBUTE_BETWEEN_UVS_LABEL: str = "Curve Distribute Between UVs"
LOFT_DISTRIBUTE_UVS_BETWEEN_EDGES_OR_UVS_LABEL: str = (
    "Loft Distribute UVs Between Edges or UVs"
)
CREATE_CURVE_FROM_EDGES_LABEL: str = "Create Curve from Edges"
CREATE_UV_CURVE_FROM_EDGES_LABEL: str = "Create Curve from Edges in UV Space"
ABOUT_WINDOW: str = "zenToolsAboutWindow"
CLOSE_CHECKBOX: str = "zenToolsCloseCheckBox"


def show_about() -> None:
    """
    Show a window with information about, and button to update/upgrade or
    uninstall, ZenTools.
    """
    if cmds.window(ABOUT_WINDOW, exists=True):
        cmds.deleteUI(ABOUT_WINDOW)
    if cmds.windowPref(ABOUT_WINDOW, exists=True):
        cmds.windowPref(ABOUT_WINDOW, remove=True)
    cmds.window(
        ABOUT_WINDOW,
        title="About ZenTools",
        height=105,
        width=237,
        resizeToFitChildren=True,
        sizeable=False,
    )
    column_layout: str = cmds.columnLayout(
        parent=ABOUT_WINDOW,
        columnOffset=("both", 10),
    )
    version: str = ""
    with contextlib.suppress(Exception):
        get_maya_zen_tools_package_info()["version"]
    cmds.text(
        label=(
            f"\nZenTools {version} © "
            f"{datetime.now(tz=timezone.utc).year} by David Belais\n"
        ).replace("  ", " "),
        align="left",
        parent=column_layout,
    )
    debugging: bool = get_tool_option(  # type: ignore
        "general", "debugging", False
    )
    # If debugging is enabled, or if ZenTools is installed as an editable
    # package, show an option to enable/disable debugging
    with contextlib.suppress(Exception):
        package_info: dict[str, str] = get_maya_zen_tools_package_info()
        if debugging or (
            package_info.get("editable_project_location") is not None
        ):
            cmds.checkBox(
                label="Enable Debugging",
                parent=column_layout,
                value=debugging,  # type: ignore
                onCommand=(
                    "from maya_zen_tools import options\n"
                    "options.set_tool_option("
                    "'general', 'debugging', "
                    "True)\n"
                    "from maya_zen_tools import _utilities\n"
                    "_utilities.reload()"
                ),
                offCommand=(
                    "from maya_zen_tools import options\n"
                    "options.set_tool_option("
                    "'general', 'debugging', "
                    "False)\n"
                    "from maya_zen_tools import _utilities\n"
                    "_utilities.reload()"
                ),
                height=30,
            )
    row_layout = cmds.rowLayout(
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
        parent=row_layout,
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
    cmds.text(
        label="",
        parent=column_layout,
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
    cmds.menuItem(label="Selection", parent=MENU, divider=True)
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
        label=SELECT_EDGES_BETWEEN_UVS_LABEL,
        command=(
            "from maya_zen_tools import loop\n"
            "loop.do_select_edges_between_uvs()"
        ),
        annotation=(
            "Selects an edge path containing the fewest edges necessary to "
            "connect selected UVs."
        ),
        parent=MENU,
    )
    cmds.menuItem(
        optionBox=True,
        command=(
            "from maya_zen_tools import loop\n"
            "loop.show_select_edges_between_uvs_options()"
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label=SELECT_UVS_BETWEEN_UVS_LABEL,
        command=(
            "from maya_zen_tools import loop\n" "loop.do_select_between_uvs()"
        ),
        annotation=(
            "Selects path containing the fewest UVs necessary to "
            "connect selected UVs."
        ),
        parent=MENU,
    )
    cmds.menuItem(
        optionBox=True,
        command=(
            "from maya_zen_tools import loop\n"
            "loop.show_select_between_uvs_options()"
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label="Flood Select",
        command="from maya_zen_tools import flood\nflood.flood_select()",
        annotation=(
            "Selected Edges will define a selection border, selected vertices "
            "or faces will determine the portion of the mesh to be selected."
        ),
        parent=MENU,
    )
    # Modeling
    cmds.menuItem(label="Modeling", parent=MENU, divider=True)
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
        label=LOFT_DISTRIBUTE_VERTICES_BETWEEN_EDGES_LABEL,
        command=(
            "from maya_zen_tools import loft\n"
            "loft.do_loft_distribute_vertices_between_edges()"
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
            "loft.show_loft_distribute_vertices_between_edges_options()"
        ),
        parent=MENU,
    )
    # Texturing
    cmds.menuItem(label="Texturing", parent=MENU, divider=True)
    cmds.menuItem(
        label=CURVE_DISTRIBUTE_BETWEEN_UVS_LABEL,
        command=(
            "from maya_zen_tools import loop\n"
            "loop.do_curve_distribute_uvs()"
        ),
        annotation="Align edge loop along a curve based on vertex selection.",
        parent=MENU,
    )
    cmds.menuItem(
        optionBox=True,
        command=(
            "from maya_zen_tools import loop\n"
            "loop.show_curve_distribute_uvs_options()"
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label=LOFT_DISTRIBUTE_UVS_BETWEEN_EDGES_OR_UVS_LABEL,
        command=(
            "from maya_zen_tools import loft\n"
            "loft.do_loft_distribute_uvs_between_edges_or_uvs()"
        ),
        annotation=("Distribute UVs between two or more parallel edge loops."),
        parent=MENU,
    )
    cmds.menuItem(
        optionBox=True,
        command=(
            "from maya_zen_tools import loft;"
            "loft.show_loft_distribute_uvs_between_edges_or_uvs_options()"
        ),
        parent=MENU,
    )
    cmds.menuItem(label="Help", parent=MENU, divider=True)
    cmds.menuItem(
        label="About ZenTools",
        command=(
            "import maya_zen_tools.menu\nmaya_zen_tools.menu.show_about()"
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label="ZenTools Documentation",
        command=(
            "import webbrowser\n"
            "webbrowser.open('https://maya-zen-tools.enorganic.org')"
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label="Reset ZenTools Options",
        command=(
            "import maya_zen_tools.options\nmaya_zen_tools.options.reset()"
        ),
        parent=MENU,
    )
    if get_tool_option("general", "debugging", False):
        # Only show these menu items if `maya-zen-tools` is an
        # editable installation (indicating it is installed for
        cmds.menuItem(label="Debugging", parent=MENU, divider=True)
        # development/testing)
        cmds.menuItem(
            label=CREATE_CURVE_FROM_EDGES_LABEL,
            command=(
                "from maya_zen_tools import loop\n"
                "loop.create_curve_from_edges()"
            ),
            annotation="Create a curve from a contiguous edge selection.",
            parent=MENU,
        )
        cmds.menuItem(
            label=CREATE_UV_CURVE_FROM_EDGES_LABEL,
            command=(
                "from maya_zen_tools import loop\n"
                "loop.create_uv_curve_from_edges()"
            ),
            annotation=(
                "Create a curve from a contiguous edge selection in UV "
                "space"
            ),
            parent=MENU,
        )
        cmds.menuItem(
            label="Reload ZenTools",
            command=(
                "from maya_zen_tools import _utilities\n_utilities.reload()"
            ),
            parent=MENU,
        )
