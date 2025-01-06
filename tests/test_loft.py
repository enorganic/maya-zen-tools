from __future__ import annotations

import pytest

from maya_zen_tools.loft import _iter_contiguous_edges


def test_iter_contiguous_edges(poly_sphere: str) -> None:
    """
    Test `flood_select`.
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


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
