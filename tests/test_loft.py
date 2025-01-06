from __future__ import annotations

import pytest
from maya import cmds  # type: ignore

from maya_zen_tools.loft import (
    _iter_contiguous_edges,
    loft_distribute_vertices_between_edges,
)


def test_iter_contiguous_edges(poly_sphere: str) -> None:
    """
    This tests `maya_zen_tools.loft._iter_contiguous_edges` with a known
    set of edge loops forming 3 contiguous segments by verifying the number
    of groupings.
    """
    assert poly_sphere == "polySphere"
    assert (
        len(
            tuple(
                _iter_contiguous_edges(
                    "polySphere.e[293]",
                    "polySphere.e[294]",
                    "polySphere.e[295]",
                    "polySphere.e[296]",
                    "polySphere.e[297]",
                    "polySphere.e[298]",
                    "polySphere.e[299]",
                    "polySphere.e[153]",
                    "polySphere.e[154]",
                    "polySphere.e[155]",
                    "polySphere.e[156]",
                    "polySphere.e[157]",
                    "polySphere.e[158]",
                    "polySphere.e[159]",
                    "polySphere.e[93]",
                    "polySphere.e[94]",
                    "polySphere.e[95]",
                    "polySphere.e[96]",
                    "polySphere.e[97]",
                    "polySphere.e[98]",
                    "polySphere.e[99]",
                )
            )
        )
        == 3
    )


def test_loft_distribute_vertices_between_edges(poly_sphere: str) -> None:
    """
    This tests `maya_zen_tools.loft.loft_distribute_vertices_between_edges` by
    moving some vertices, then selecting vertices along known contiguous edge
    loop segments and executing the loft.
    """
    assert poly_sphere == "polySphere"
    cmds.select(
        "polySphere.e[293]",
        "polySphere.e[294]",
        "polySphere.e[295]",
        "polySphere.e[296]",
        "polySphere.e[297]",
        "polySphere.e[298]",
        "polySphere.e[299]",
        "polySphere.e[153]",
        "polySphere.e[154]",
        "polySphere.e[155]",
        "polySphere.e[156]",
        "polySphere.e[157]",
        "polySphere.e[158]",
        "polySphere.e[159]",
        "polySphere.e[93]",
        "polySphere.e[94]",
        "polySphere.e[95]",
        "polySphere.e[96]",
        "polySphere.e[97]",
        "polySphere.e[98]",
        "polySphere.e[99]",
    )
    loft_distribute_vertices_between_edges()


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
