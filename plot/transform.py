import numpy as np


def assign_where_not_zero(arr, assign):
    arr_copy = np.copy(arr)

    arr_len = arr_copy[arr_copy != 0.0].shape[0]
    assign_arr_len = assign.shape[0]

    if arr_len == assign_arr_len:
        arr_copy[arr_copy != 0.0] = assign
    else:
        arr_copy[arr_copy != 0.0] = assign[:arr_len - assign_arr_len]
    return arr_copy
