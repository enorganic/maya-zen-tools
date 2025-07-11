"""
This module modifies your userSetup.py script to add startup procedures
needed to use ZenTools.
"""

from __future__ import annotations

import argparse

from maya_zen_tools._utilities import (
    check_call,
    get_maya_zen_tools_package_info,
    reload,
    which_mayapy,
)


def upgrade() -> None:
    """
    Install the most recent version of ZenTools for Maya
    """
    # Check to see if the currently installed package is editable
    package_info: dict[str, str] = get_maya_zen_tools_package_info()
    if package_info.get("editable_project_location") is not None:
        # Don't upgrade if installed in editable mode (for development)
        return
    check_call(
        [
            str(which_mayapy()),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--upgrade-strategy",
            "eager",
            "maya-zen-tools",
        ]
    )
    updated_package_info: dict[str, str] = get_maya_zen_tools_package_info()
    if updated_package_info["version"] != package_info["version"]:
        # Reload all maya_zen_tools modules
        reload()
        # Re-install ZenTools for maya
        from maya_zen_tools import install

        install.main()


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="maya-zen-tools upgrade",
        description="Upgrade ZenTools for Maya",
    )
    parser.parse_args()
    upgrade()


if __name__ == "__main__":
    main()
