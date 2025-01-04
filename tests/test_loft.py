from __future__ import annotations

import maya.standalone  # type: ignore
import pytest

from maya_zen_tools.loft import _iter_contiguous_edges

maya.standalone.initialize(name="python")
from maya import cmds  # type: ignore  # noqa: E402

from maya_zen_tools import startup  # noqa


def test_iter_contiguous_edges() -> None:
    """
    Test `flood_select`.
    """
    cmds.select(clear=True)
    poly_sphere: str = cmds.polySphere(constructionHistory=False)[0]
    edges: set[str] = {
        f"{poly_sphere}.e[310]",
        f"{poly_sphere}.e[311]",
        f"{poly_sphere}.e[312]",
        f"{poly_sphere}.e[313]",
        f"{poly_sphere}.e[314]",
        f"{poly_sphere}.e[315]",
        f"{poly_sphere}.e[210]",
        f"{poly_sphere}.e[211]",
        f"{poly_sphere}.e[212]",
        f"{poly_sphere}.e[213]",
        f"{poly_sphere}.e[214]",
        f"{poly_sphere}.e[215]",
        f"{poly_sphere}.e[110]",
        f"{poly_sphere}.e[111]",
        f"{poly_sphere}.e[112]",
        f"{poly_sphere}.e[113]",
        f"{poly_sphere}.e[114]",
        f"{poly_sphere}.e[115]",
    }
    assert len(tuple(_iter_contiguous_edges(*edges))) == 3


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
