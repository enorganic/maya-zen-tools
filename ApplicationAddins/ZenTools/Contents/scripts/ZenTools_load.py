"""
This script will check to see if the `maya-zen-tools` python package
is installed, and if not, install it—otherwise, it will load the add-in.
"""

import os
from pathlib import Path
from subprocess import check_call

try:
    from maya_zen_tools import startup
except ImportError:
    print("Installing ZenTools for Maya")
    mayapy: str = str(
        Path(os.environ.get("MAYA_LOCATION")).joinpath("bin", "mayapy")
    )
    check_call([mayapy, "-m", "pip", "install", "maya-zen-tools"])
    check_call([mayapy, "-m", "maya_zen_tools", "install"])
    from maya_zen_tools import startup

    startup.main()
