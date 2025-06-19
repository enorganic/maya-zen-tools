import argparse
from pathlib import Path
from platform import system

MAYAPY_TEMPLATE: str = {
    "Windows": r"C:\Program Files\Autodesk\Maya{version}\bin\mayapy",
    "Linux": "/usr/autodesk/Maya{version}/bin/mayapy",
    "Darwin": (
        "/Applications/Autodesk/maya{version}/Maya.app/Contents/bin/mayapy"
    ),
}[system()]


def which_mayapy(version: str, *, directory: bool = False) -> str:
    """
    Get the file path to the mayapy executable for a given Maya version, or
    it's parent directory if `directory` is True.
    """
    path: str = MAYAPY_TEMPLATE.format(version=version)
    return str(Path(path).parent) if directory else path


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="scripts/which_mayapy.py",
        description=(
            "Print the path to the mayapy executable for a given Maya version."
        ),
    )
    parser.add_argument(
        "version",
        type=str,
        help=(
            "The Autodesk Maya major version (e.g., 2023, 2024, 2025, 2026) "
            "for which to find a mayapy executable."
        ),
    )
    parser.add_argument(
        "-d",
        "--directory",
        action="store_true",
        help="Return the directory rather than the executable path.",
    )
    namespace: argparse.Namespace = parser.parse_args()
    print(which_mayapy(namespace.version, directory=namespace.directory))


if __name__ == "__main__":
    main()
