import numpy as np


def softmax(x, axis=None):
    m = np.max(x, axis=axis, keepdims=True)
    e_x = np.exp(x - m)
    sum = np.sum(e_x, axis=axis, keepdims=True)
    f_x = e_x / sum
    return f_x


def confusion_matrix(y_true, y_pred, percentage=False):
    n_labels = len(set.union(set(y_true), set(y_pred)))
    cm = np.zeros((n_labels, n_labels))
    for true, pred in zip(y_true, y_pred):
        cm[true, pred] += 1
    if percentage:
        return softmax(cm, axis=-1)
    return cm
