"""
This module modifies your userSetup.py script to add startup procedures
needed to use ZenTools.
"""

from __future__ import annotations

import argparse
import re
from subprocess import check_call
from typing import TYPE_CHECKING

from maya import cmds  # type: ignore

from maya_zen_tools._utilities import find_user_setup_py, which_mayapy
from maya_zen_tools.menu import MENU

if TYPE_CHECKING:
    from pathlib import Path


def uninstall() -> None:
    """
    Uninstall ZenTools for Maya
    """
    user_setup_py: str = ""
    user_setup_py_path: Path = find_user_setup_py()
    if user_setup_py_path.is_file():
        with open(user_setup_py_path) as user_setup_py_io:
            user_setup_py = user_setup_py_io.read()
    # Remove the ZenTools startup line from userSetup.py
    if user_setup_py:
        with open(user_setup_py_path, "w") as user_setup_py_io:
            user_setup_py_io.write(
                re.sub(
                    r"(^|\n)from maya_zen_tools import startup(\n|$)",
                    r"\1",
                    user_setup_py,
                )
            )
    # Uninstall the `maya-zen-tools` package
    check_call(
        [
            str(which_mayapy()),
            "-m",
            "pip",
            "uninstall",
            "-y",
            "maya-zen-tools",
        ]
    )
    # Delete the ZenTools menu
    cmds.deleteUI(MENU)


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="maya-zen-tools uninstall",
        description="Uninstall ZenTools for Maya",
    )
    parser.parse_args()
    uninstall()


if __name__ == "__main__":
    main()
