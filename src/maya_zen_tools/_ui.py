from __future__ import annotations

from maya import cmds  # type: ignore

WINDOW: str = "zenToolsWindow"
CONFIRMATION_WINDOW: str = "zenToolsConfirmationWindow"


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
    # Create the window
    if cmds.window(CONFIRMATION_WINDOW, exists=True):
        cmds.deleteUI(CONFIRMATION_WINDOW)
    if cmds.windowPref(CONFIRMATION_WINDOW, exists=True):
        cmds.windowPref(CONFIRMATION_WINDOW, remove=True)
    cmds.window(
        CONFIRMATION_WINDOW,
        title=title or label,
        resizeToFitChildren=True,
        sizeable=False,
        width=340,
    )
    column_layout: str = cmds.columnLayout(
        parent=CONFIRMATION_WINDOW,
        columnOffset=("both", 10),
    )
    cmds.text(
        label=f"\n{label.strip()}\n",
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
            f"cmds.deleteUI('{CONFIRMATION_WINDOW}')"
        ),
    )
    cmds.button(
        label="Cancel",
        parent=row_layout,
        command=(
            f"{cancel_command}\n"
            "from maya import cmds\n"
            f"cmds.deleteUI('{CONFIRMATION_WINDOW}')"
        ),
    )
    cmds.text(
        label="",
        parent=column_layout,
    )
    cmds.showWindow(CONFIRMATION_WINDOW)


def set_wait_cursor_state(state: bool) -> None:  # noqa: FBT001
    """
    Set the wait cursor state.

    Parameters:
        state: True to set the wait to "on", False to turn it off.
    """
    if state and not cmds.waitCursor(query=True, state=True):
        cmds.waitCursor(state=True)
    else:
        while cmds.waitCursor(query=True, state=True):
            cmds.waitCursor(state=False)
