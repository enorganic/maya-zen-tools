from __future__ import annotations

from typing import Sequence


class ZenToolsWarning(Warning):
    pass


class MultipleVertexPathsPossibleWarning(ZenToolsWarning):
    pass


class ZenToolsError(Exception):
    """
    Base class for ZenTools Exceptions
    """


class InvalidSelectionError(Exception):
    pass


class EdgesNotOnSameRingError(InvalidSelectionError):
    def __init__(self, shape: str, edge_ids: tuple[int, int]) -> None:
        self.shape: str = shape
        self.edge_ids: tuple[int, ...] = edge_ids
        super().__init__(
            "Edges are not on the same ring: "
            f'("{shape}.e[{edge_ids[0]}]", "{shape}.e[{edge_ids[1]}]")'
        )


class NonLinearSelectionError(InvalidSelectionError):
    pass


class NonContiguousMeshSelectionError(InvalidSelectionError):
    pass


class TooManyShapesError(InvalidSelectionError):
    """
    Raised when a loop or loft is attempted using
    components from more than one polygon mesh.
    """

    def __init__(self, shapes: Sequence[str]) -> None:
        self.shapes: tuple[str, ...] = tuple(shapes)
        super().__init__(shapes)

    def __repr__(self) -> str:
        return (
            f"TooManyShapesError({self.shapes!r}): "
            "Selected components must all belong to the same shape."
        )

    def __str__(self) -> str:
        return repr(self)


def _get_about() -> str:
    from maya import cmds  # type: ignore

    return (
        f"Maya Version: {cmds.about(installedVersion=True)}\n"
        f"Operating System: {cmds.about(operatingSystem=True)}\n"
        f"Loaded modules: {cmds.moduleInfo(listModules=True)}\n"
        f"Loaded plugins: {cmds.pluginInfo(q=True, listPlugins=True)}\n"
        f"API Version: {cmds.about(apiVersion=True)}\n"
        f"Build Variant: {cmds.about(buildVariant=True)}\n"
        f"Creative Version: {cmds.about(creativeVersion=True)}\n"
        f"Custom Version: {cmds.about(customVersionString=True)}\n"
        f"Cut Identifier: {cmds.about(cutIdentifier=True)}\n"
    )


class CreateNodeError(ValueError):
    def __init__(self, node_type: str) -> None:
        super().__init__(
            f'"{node_type}" is an unknown node type.\n' f"{_get_about()}"
        )
