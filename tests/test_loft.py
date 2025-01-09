from __future__ import annotations

import pytest
from maya import cmds  # type: ignore

from maya_zen_tools._traverse import iter_aligned_contiguous_edges
from maya_zen_tools.loft import (
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
                iter_aligned_contiguous_edges(
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


def test_loft_distribute_vertices_between_edges_poly_sphere_lattitude(
    poly_sphere: str,
) -> None:
    """
    This tests `maya_zen_tools.loft.loft_distribute_vertices_between_edges` by
    verifying affected faces.
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


def test_loft_distribute_vertices_between_edges_poly_sphere_longitude(
    poly_sphere: str,
) -> None:
    """
    This tests `maya_zen_tools.loft.loft_distribute_vertices_between_edges` by
    verifying affected faces.
    """
    assert poly_sphere == "polySphere"
    cmds.select(
        "polySphere.e[480]",
        "polySphere.e[500]",
        "polySphere.e[520]",
        "polySphere.e[540]",
        "polySphere.e[560]",
        "polySphere.e[580]",
        "polySphere.e[600]",
        "polySphere.e[620]",
        "polySphere.e[640]",
        "polySphere.e[660]",
        "polySphere.e[680]",
        "polySphere.e[497]",
        "polySphere.e[517]",
        "polySphere.e[537]",
        "polySphere.e[557]",
        "polySphere.e[577]",
        "polySphere.e[597]",
        "polySphere.e[617]",
        "polySphere.e[637]",
        "polySphere.e[657]",
        "polySphere.e[677]",
        "polySphere.e[697]",
        "polySphere.e[493]",
        "polySphere.e[513]",
        "polySphere.e[533]",
        "polySphere.e[553]",
        "polySphere.e[573]",
        "polySphere.e[593]",
        "polySphere.e[613]",
        "polySphere.e[633]",
        "polySphere.e[653]",
        "polySphere.e[673]",
        "polySphere.e[693]",
    )
    assert set(loft_distribute_vertices_between_edges()[0]) == {
        "polySphere.f[113]",
        "polySphere.f[114]",
        "polySphere.f[115]",
        "polySphere.f[116]",
        "polySphere.f[117]",
        "polySphere.f[118]",
        "polySphere.f[119]",
        "polySphere.f[133]",
        "polySphere.f[134]",
        "polySphere.f[135]",
        "polySphere.f[136]",
        "polySphere.f[137]",
        "polySphere.f[138]",
        "polySphere.f[139]",
        "polySphere.f[153]",
        "polySphere.f[154]",
        "polySphere.f[155]",
        "polySphere.f[156]",
        "polySphere.f[157]",
        "polySphere.f[158]",
        "polySphere.f[159]",
        "polySphere.f[173]",
        "polySphere.f[174]",
        "polySphere.f[175]",
        "polySphere.f[176]",
        "polySphere.f[177]",
        "polySphere.f[178]",
        "polySphere.f[179]",
        "polySphere.f[193]",
        "polySphere.f[194]",
        "polySphere.f[195]",
        "polySphere.f[196]",
        "polySphere.f[197]",
        "polySphere.f[198]",
        "polySphere.f[199]",
        "polySphere.f[213]",
        "polySphere.f[214]",
        "polySphere.f[215]",
        "polySphere.f[216]",
        "polySphere.f[217]",
        "polySphere.f[218]",
        "polySphere.f[219]",
        "polySphere.f[233]",
        "polySphere.f[234]",
        "polySphere.f[235]",
        "polySphere.f[236]",
        "polySphere.f[237]",
        "polySphere.f[238]",
        "polySphere.f[239]",
        "polySphere.f[253]",
        "polySphere.f[254]",
        "polySphere.f[255]",
        "polySphere.f[256]",
        "polySphere.f[257]",
        "polySphere.f[258]",
        "polySphere.f[259]",
        "polySphere.f[273]",
        "polySphere.f[274]",
        "polySphere.f[275]",
        "polySphere.f[276]",
        "polySphere.f[277]",
        "polySphere.f[278]",
        "polySphere.f[279]",
        "polySphere.f[293]",
        "polySphere.f[294]",
        "polySphere.f[295]",
        "polySphere.f[296]",
        "polySphere.f[297]",
        "polySphere.f[298]",
        "polySphere.f[299]",
        "polySphere.f[313]",
        "polySphere.f[314]",
        "polySphere.f[315]",
        "polySphere.f[316]",
        "polySphere.f[317]",
        "polySphere.f[318]",
        "polySphere.f[319]",
    }


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
