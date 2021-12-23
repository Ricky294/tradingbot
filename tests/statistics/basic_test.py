import numpy as np

from statistics.basic import all_time_high


def test_all_time_high():
    x, y = all_time_high(
        np.array([1, 2, 3, 4, 5]),
        np.array([2, 4, 8, 1, 4]),
    )
    assert x == 3
    assert y == 8


def test_all_time_low():
    x, y = all_time_high(
        np.array([1, 2, 3, 4, 5]),
        np.array([2, 4, 8, 1, 4]),
    )
    assert x == 4
    assert y == 1


def test_return_on_hold_ratio_from_start_to_present():
    x = return_on_hold_ratio_from_start_to_present(np.array([5, 10, 20, 50]))
    assert x == 10


