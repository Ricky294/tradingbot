from abc import ABC, abstractmethod
from typing import Callable, Tuple

import numpy as np

from trader.core.util.common import Storable


class SLTPIndicator(ABC, Callable, Storable):
    @abstractmethod
    def __init__(self, *args, **data): ...

    @abstractmethod
    def __call__(self, candles: np.ndarray, side: int, leverage: int) -> Tuple[float, float]: ...
