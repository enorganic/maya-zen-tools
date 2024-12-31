"""
This module modifies your userSetup.py script to add startup procedures
needed to use ZenTools.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

has_maya_cmds: bool = True
try:
    from maya import cmds  # type: ignore
except ImportError:
    has_maya_cmds = False


def _find_user_setup_py() -> Path:
    """
    Find the userSetup.py script
    """
    scripts_directory: Path
    if has_maya_cmds:
        scripts_directory = Path(cmds.internalVar(userScriptDir=True))
    else:
        # If `maya.cmds`` is not available, we have to install
        # using the non-version-specific Maya scripts directory,
        # as we don't know which version to target
        maya_app_dir: str | None = os.environ.get("MAYA_APP_DIR")
        if not maya_app_dir:
            maya_app_dir = (
                os.path.expanduser("~/Library/Preferences/Autodesk/Maya")
                if sys.platform == "darwin"
                else os.path.expanduser("~/Documents/Maya")
                if sys.platform.startswith("win")
                else os.path.expanduser("~/Maya")
            )
        scripts_directory = Path(maya_app_dir) / "scripts"
    os.makedirs(scripts_directory, exist_ok=True)
    return scripts_directory / "userSetup.py"


def install() -> None:
    """
    Add the line "from maya_zen_tools import startup" to userSetup.py,
    if it isn't already in the script.
    """
    user_setup_py: str = ""
    user_setup_py_path: Path = _find_user_setup_py()
    if user_setup_py_path.is_file():
        with open(user_setup_py_path) as user_setup_py_io:
            user_setup_py = user_setup_py_io.read()
    if not (
        user_setup_py
        and re.search(
            r"(^|\n)from maya_zen_tools import startup\n", user_setup_py
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
