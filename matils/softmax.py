import numpy as np


def softmax(arr, axis=None):
    max_val = np.max(arr, axis=axis, keepdims=True)
    e_x = np.exp(arr - max_val)
    sum_val = np.sum(e_x, axis=axis, keepdims=True)
    f_x = e_x / sum_val
    return f_x
