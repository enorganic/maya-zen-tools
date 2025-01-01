from __future__ import annotations

import contextlib
import importlib
import sys
from traceback import format_exception
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

import os
from pathlib import Path

has_maya_cmds: bool = True
try:
    from maya import cmds  # type: ignore
except ImportError:
    has_maya_cmds = False


def reload() -> None:
    """
    Reload all ZenTools modules
    """
    name: str
    module: ModuleType
    for name, module in tuple(sys.modules.items()):
        if name.startswith("maya_zen_tools.") or (name == "maya_zen_tools"):
            with contextlib.suppress(ModuleNotFoundError):
                importlib.reload(module)


def get_exception_text() -> str:
    """
    When called within an exception, this function returns a text
    representation of the error matching what is found in
    `traceback.print_exception`, but is returned as a string value rather than
    printing.
    """
    return "".join(format_exception(*sys.exc_info()))


def find_user_setup_py() -> Path:
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
