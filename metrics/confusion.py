import numpy as np

from matils import softmax


def confusion_matrix(y_true, y_pred, percentage=False):
    n_labels = len(set.union(set(y_true), set(y_pred)))
    cm = np.zeros((n_labels, n_labels))
    for true, pred in zip(y_true, y_pred):
        cm[true, pred] += 1
    if percentage:
        return softmax(cm, axis=-1)
    return cm
