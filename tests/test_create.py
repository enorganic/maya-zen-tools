from __future__ import annotations

import pytest

from maya_zen_tools._create import create_node
from maya_zen_tools.errors import CreateNodeError


def test_create_node_error() -> None:
    """
    Verify that attempting to create an unknown node type will raise an error
    """
    create_node_error: CreateNodeError | None = None
    try:
        create_node("nonsense")
    except CreateNodeError as error:
        create_node_error = error
    assert create_node_error is not None


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
