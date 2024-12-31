from __future__ import annotations

from maya import cmds  # type: ignore

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
        command=("from maya_zen_tools import loop;loop.do_select_loop()"),
        annotation=(
            "Selects an edge path containing the fewest edges necessary to "
            "connect selected vertices."
        ),
        parent=MENU,
    )
    cmds.menuItem(
        label="Flood Select",
        command=("from maya_zen_tools import select;select.do_flood_select()"),
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
