from abc import ABC, abstractmethod
from typing import Callable

import numpy as np


class Indicator(ABC, Callable):
    @abstractmethod
    def __init__(self, *args, **data):
        pass

    @abstractmethod
    def __call__(self, candles: np.ndarray) -> np.ndarray:
        pass
