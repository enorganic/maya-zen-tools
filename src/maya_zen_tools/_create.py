from __future__ import annotations

from maya import cmds  # type: ignore


def create_locator(
    *,
    translate: tuple[float, float, float] | None = None,
    scale: float = 1.0,
    connect_translate: str | tuple[str] | None = None,
) -> str:
    """
    Create a locator at the given translation.

    Parameters:
        translation: The translation of the locator.
        scale: The scale of the locator.
    """
    locator: str = cmds.spaceLocator(name="zenLoopLocator#")[0]
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
    return locator
