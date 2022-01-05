import numpy as np


def assign_where_not_zero(arr, assign):
    arr_copy = np.copy(arr)
    arr_copy[arr_copy != 0.0] = assign

    return arr_copy
