from __future__ import annotations

import contextlib
import functools
import importlib
import json
import subprocess
import sys
from traceback import format_exception
from typing import TYPE_CHECKING, Any, Callable, Iterable

if TYPE_CHECKING:
    from types import ModuleType

import os
from pathlib import Path

has_maya_cmds: bool = True
try:
    from maya import cmds  # type: ignore

    has_maya_cmds = hasattr(cmds, "internalVar")
except ImportError:
    has_maya_cmds = False

MAYA_ZEN_TOOLS: str = "maya-zen-tools"


def which_mayapy() -> Path:
    maya_location: str | None = os.environ.get("MAYA_LOCATION")
    if maya_location:
        return Path(maya_location).joinpath("bin", "mayapy")
    return Path(sys.executable)


def reload() -> None:
    """
    Reload all ZenTools modules
    """
    name: str
    module: ModuleType
    for name, module in tuple(sys.modules.items()):
        if name.startswith("maya_zen_tools.") or name == "maya_zen_tools":
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
                else (
                    os.path.expanduser("~/Documents/Maya")
                    if sys.platform.startswith("win")
                    else os.path.expanduser("~/Maya")
                )
            )
        scripts_directory = Path(maya_app_dir) / "scripts"
    os.makedirs(scripts_directory, exist_ok=True)
    return scripts_directory / "userSetup.py"


def find_zen_tools_package_directory() -> Path | None:
    """
    Return the path to the Autodesk Marketplace package, if that is how
    maya-zen-tools has been installed.
    """
    path: Path
    for path in map(
        Path, os.environ.get("MAYA_SCRIPT_PATH", "").split(os.path.pathsep)
    ):
        grand_parent: Path = path.parent.parent
        if grand_parent.name == "ZenTools":
            return grand_parent
    return None


@functools.wraps(subprocess.check_output)
def check_output(*args: Any, **kwargs: Any) -> str:
    """
    A wrapper around `subprocess.check_output` which will not open a console
    window on Windows.
    """
    if sys.platform.startswith("win"):
        kwargs["creationflags"] = (
            kwargs.get("creationflags", 0) | subprocess.CREATE_NO_WINDOW
        )
    return subprocess.check_output(
        *args,
        **kwargs,
    )


@functools.wraps(subprocess.check_call)
def check_call(*args: Any, **kwargs: Any) -> int:
    """
    A wrapper around `subprocess.check_call` which will not open a console
    window on Windows.
    """
    if sys.platform.startswith("win"):
        kwargs["creationflags"] = (
            kwargs.get("creationflags", 0) | subprocess.CREATE_NO_WINDOW
        )
    return subprocess.check_call(
        *args,
        **kwargs,
    )


def get_maya_zen_tools_package_info() -> dict[str, str]:
    package_info: dict[str, str]
    for package_info in json.loads(
        check_output(
            [str(which_mayapy()), "-m", "pip", "list", "--format", "json"],
            text=True,
        ).strip()
    ):
        if package_info["name"] == MAYA_ZEN_TOOLS:
            return package_info
    raise KeyError(MAYA_ZEN_TOOLS)


def as_tuple(
    user_function: Callable[..., Iterable[Any]],
) -> Callable[..., tuple[Any, ...]]:
    """
    This is a decorator which will return an iterable as a tuple.
    """

    def wrapper(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        return tuple(user_function(*args, **kwargs) or ())

    return functools.update_wrapper(wrapper, user_function)
