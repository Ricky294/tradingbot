import numpy as np

from util.numpy import cross_signal


def test_nan_cross_signal():
    arr = np.array([np.nan, np.nan, np.nan, 20])
    signal = cross_signal(arr, "<", 15)

    expected = np.array([False, False, False, False])

    assert np.array_equal(expected, signal)


def test_empty_cross_signal():
    arr = np.array([])
    signal = cross_signal(arr, ">", 15)

    expected = np.array([])

    assert np.array_equal(expected, signal)


def test_size_1_cross_signal():
    arr = np.array([1])
    signal = cross_signal(arr, ">", 15)
    expected = np.array([False])
    assert np.array_equal(expected, signal)

    arr = np.array([1])
    signal = cross_signal(arr, "<", 15)
    expected = np.array([True])
    assert np.array_equal(expected, signal)


def test_size_2_cross_signal():
    arr = np.array([1, 20])
    signal = cross_signal(arr, ">", 15)
    expected = np.array([False, True])
    assert np.array_equal(expected, signal)


def test_const_cross_signal():
    arr = np.array([10, 15, 20, 25, 8, 14, 16, 18])
    signal = cross_signal(arr, ">", 15)

    expected = np.array([False, False, True, False, False, False, True, False])

    assert np.array_equal(expected, signal)


def test_array_cross_signal():
    arr = np.array([10, 15, 20, 25, 8, 14, 16, 18])
    arr2 = np.array([8, 10, 25, 30, 20, 13, 12, 20])

    signal = cross_signal(arr, "<", arr2)
    expected = np.array([False, False, True, False, False, False, False, True])

    assert np.array_equal(expected, signal)


def test_empty_array_cross_signal():
    arr = np.array([])
    arr2 = np.array([])

    signal = cross_signal(arr, "<", arr2)
    expected = np.array([])

    assert np.array_equal(expected, signal)


def test_array_1_cross_signal():
    arr = np.array([5])
    arr2 = np.array([1])

    signal = cross_signal(arr, "<", arr2)
    expected = np.array([False])

    assert np.array_equal(expected, signal)
