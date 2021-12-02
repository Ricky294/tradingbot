from typing import Union

import numpy as np

from util import compare


def cross_signal(
    arr: np.ndarray, logical_operator: str, other: Union[float, np.ndarray]
) -> np.array:
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
