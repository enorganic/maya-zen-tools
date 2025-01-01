"""
This module modifies your userSetup.py script to add startup procedures
needed to use ZenTools.
"""

from __future__ import annotations

import argparse
import sys
from subprocess import check_call

from maya_zen_tools._utilities import reload


def upgrade() -> None:
    """
    Install the most recent version of ZenTools for Maya
    """
    check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--upgrade-strategy",
            "eager",
            "maya-zen-tools",
        ]
    )
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
