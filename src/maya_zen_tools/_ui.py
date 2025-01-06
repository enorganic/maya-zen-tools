from __future__ import annotations

from maya import cmds  # type: ignore

WINDOW: str = "zenToolsWindow"


def show_confirmation_dialogue(
    label: str,
    yes_command: str,
    cancel_command: str = "",
    title: str = "",
) -> None:
    """
    Show a dialogue asking for confirmation of an operation.

    Parameters:
        text: The text to display
        yes_command: The command to execute if the user clicks "Yes".
        cancel_command: The command to execute if the user clicks "Cancel".
        title: The title for the dialogue window.
    """
    window: str = cmds.window(title=title or label)
    column_layout: str = cmds.columnLayout(parent=window, margins=15)
    cmds.text(
        label=f"{label.rstrip()}\n",
        align="left",
        parent=column_layout,
    )
    row_layout: str = cmds.rowLayout(parent=column_layout, numberOfColumns=2)
    cmds.button(
        label="Yes",
        parent=row_layout,
        command=(
            f"{yes_command}\n"
            "from maya import cmds\n"
            f"cmds.deleteUI('{window}')"
        ),
    )
    cmds.button(
        label="Cancel",
        parent=row_layout,
        command=(
            f"{cancel_command}\n"
            "from maya import cmds\n"
            f"cmds.deleteUI('{window}')"
        ),
    )
    cmds.showWindow(window)
