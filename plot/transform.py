import numpy as np


def assign_where_not_zero(arr, assign):
    arr_copy = np.copy(arr)
    try:
        arr_copy[arr_copy != 0.0] = assign
    except ValueError:
        arr_copy[arr_copy != 0.0] = assign[:-1]
    return arr_copy
