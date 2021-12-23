import numpy as np


def normalize_around_price(data_sequence: np.ndarray, *other_sequences, price: float):
    data_sequence = data_sequence - price
    lo = np.min(data_sequence)
    hi = np.max(data_sequence)
    dist = (hi - lo)
    data_sequence = data_sequence / dist
    if other_sequences:
        sequences = tuple((seq - price) / dist for seq in other_sequences)
        return data_sequence, *sequences
    return data_sequence


def normalize(data_sequence: np.ndarray, *other_sequences):
    lo = np.min(data_sequence)
    hi = np.max(data_sequence)
    dist = (hi - lo)
    data_sequence = data_sequence - lo
    data_sequence = data_sequence / dist
    if other_sequences:
        sequences = tuple((seq - lo) / dist for seq in other_sequences)
        return data_sequence, *sequences
    return data_sequence
