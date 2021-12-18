from typing import Union

import numpy as np

from util import compare


def cross_signal(
    arr: np.ndarray, logical_operator: str, other: Union[float, np.ndarray]
) -> np.array:

    if arr.size == 0:
        return np.array([])
    if arr.size == 1:
        if isinstance(other, np.ndarray):
            return np.array([compare(arr[0], logical_operator, other[0])])
        return np.array([compare(arr[0], logical_operator, other)])

    sliding_array = np.lib.stride_tricks.sliding_window_view(arr, (2,))

    if isinstance(other, np.ndarray):
        other = np.lib.stride_tricks.sliding_window_view(other, (2,))
        first_value = compare(sliding_array[0], logical_operator, other[0])
    else:
        first_value = compare(sliding_array[0], logical_operator, other)

    bool_sliding_array = compare(sliding_array, logical_operator, other)

    x = np.insert(
        (np.array(bool_sliding_array) == [False, True]), 0, first_value, axis=0
    )
    return x.all(axis=-1)


def map_match(src, tar):
    src_size = np.shape(src)[0]
    tar_size = np.shape(tar)[0]
    src_mat = src[:, np.newaxis]
    tar_mat = np.reshape(np.tile(tar, src_size), newshape=(src_size, tar_size))
    mask = np.sum(np.equal(src_mat, tar_mat), axis=-1)
    return src * mask


def mask_match(src, tar):
    src_size = np.shape(src)[0]
    tar_size = np.shape(tar)[0]
    src_mat = src[:, np.newaxis]
    tar_mat = np.reshape(np.tile(tar, src_size), newshape=(src_size, tar_size))
    return np.any(np.equal(src_mat, tar_mat), axis=-1)
