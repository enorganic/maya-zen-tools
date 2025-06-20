from __future__ import annotations

import sys
from pathlib import Path
from shutil import copytree, rmtree

ROOT_PATH: Path = Path(__file__).parent.parent
INSTALL_PATH: Path | None = (
    "/Users/Shared/Autodesk/ApplicationAddins/ZenTools"
    if sys.platform == "darwin"
    else None  # TODO: windows add-in install
    if sys.platform.startswith("win")
    else None  # TODO: linux add-in install
    if sys.platform == "linux"
    else None
)


def main() -> None:
    rmtree(INSTALL_PATH, ignore_errors=True)
    copytree(ROOT_PATH / "ApplicationAddins/ZenTools", INSTALL_PATH)


if __name__ == "__main__":
    main()
