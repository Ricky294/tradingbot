from abc import abstractmethod
from typing import Callable

import numpy as np

from abstract import FuturesTrader


class Strategy(Callable):
    def __init__(self, symbol: str, trader: FuturesTrader):
        self.symbol = symbol.upper()
        self.trader = trader

    @abstractmethod
    def __call__(
        self,
        candles: np.ndarray,
    ): ...
