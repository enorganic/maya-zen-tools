"""
This module modifies your userSetup.py script to add startup procedures
needed to use ZenTools.
"""

from __future__ import annotations

import argparse
import re
from typing import TYPE_CHECKING

from maya_zen_tools._utilities import (
    find_user_setup_py,
    find_zen_tools_package_directory,
)

if TYPE_CHECKING:
    from pathlib import Path


def install() -> None:
    """
    Check to see if the ZenTools Autodesk marketplace add-in
    is installed, and if not—add the line "from maya_zen_tools import startup"
    to userSetup.py (if it isn't already in the script).
    """
    if find_zen_tools_package_directory():
        # If there's a package—we don't need to look for a userSetup.py script.
        return
    user_setup_py: str = ""
    user_setup_py_path: Path = find_user_setup_py()
    if user_setup_py_path.is_file():
        with open(user_setup_py_path) as user_setup_py_io:
            user_setup_py = user_setup_py_io.read()
    if not (
        user_setup_py
        and re.search(
            r"(^|\n)from maya_zen_tools import startup(\n|$)", user_setup_py
        )
    ):
        with open(user_setup_py_path, "a") as user_setup_py_io:
            user_setup_py_io.write("from maya_zen_tools import startup\n")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="maya-zen-tools install",
        description="Install ZenTools for Maya",
    )
    parser.parse_args()
    install()


if __name__ == "__main__":
    main()
