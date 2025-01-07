import pytest

from maya_zen_tools._traverse import get_distance_between


def test_get_distance_between() -> None:
    assert get_distance_between((0, 0, 0), (1, 1, 1)) == 1.7320508075688772
    assert get_distance_between((3, -6, 9), (5, 12, 24)) == 23.515952032609693
    assert get_distance_between((5, 12, 24), (33, 5, 19)) == 29.29163703175362
    assert get_distance_between((3, -6, 9), (5, 12, 24), (33, 5, 19)) == (
        52.80758906436331
    )


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
