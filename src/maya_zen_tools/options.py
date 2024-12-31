from __future__ import annotations

import json
from pathlib import Path

from maya import cmds  # type: ignore

OPTIONS_PATH: Path = Path(cmds.internalVar(userPrefDir=True)) / "ZenTools.json"


class Options:
    def __init__(self) -> None:
        self._dict: dict[str, dict[str, str | int | float]] = {}

    def gets(
        self,
        tool: str,
    ) -> dict[str, bool | str | int | float]:
        """
        Get all options for a tool.
        """
        if (not self._dict) and OPTIONS_PATH.is_file():
            with open(OPTIONS_PATH) as options_io:
                self._dict = json.load(options_io)
        if tool not in self._dict:
            self._dict[tool] = {}
        return self._dict[tool]

    def get(
        self, tool: str, option: str, default: float | str | bool | None = None
    ) -> bool | str | float | None:
        """
        Get a single option for a tool.
        """
        return self.gets(tool).get(option, default)

    def sets(
        self, tool: str, options_values: dict[str, bool | str | int | float]
    ) -> None:
        """
        Set all options for a tool.
        """
        self._dict[tool] = options_values
        self.save()

    def set(self, tool: str, option: str, value: bool | float | str) -> None:
        """
        Set a tool option.
        """
        if tool not in self._dict:
            self._dict[tool] = {}
        self._dict[tool][option] = value
        self.save()

    def save(self) -> None:
        """
        Writes options to disk
        """
        with open(OPTIONS_PATH, "w") as options_io:
            json.dump(self._dict, options_io, indent=4)


options: Options = Options()
