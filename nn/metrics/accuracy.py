import torch as pt


def accuracy_function(real: pt.Tensor, predictions: pt.Tensor):
    acc = pt.sum(pt.argmax(predictions, dim=-1) == real) / real.shape[-1]
    return acc


def label_accuracy_function(real: pt.Tensor, predictions: pt.Tensor, label: int):
    preds = pt.argmax(predictions, dim=-1)
    label_mask = real == label
    label_acc = pt.logical_and(preds == real, label_mask)
    label_sum = pt.sum(label_mask)
    acc = pt.sum(label_acc) / label_sum
    return acc
