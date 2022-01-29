from abc import abstractmethod
from typing import Callable

import numpy as np

from trader.core.interface import FuturesTrader
from trader.core.util.trade import calculate_quantity


class Strategy(Callable):

    def __init__(
            self,
            symbol: str,
            trader: FuturesTrader,
            trade_ratio: float,
            asset="USDT",
            leverage=1,
            *args, **kwargs,
    ):
        self.symbol = symbol.upper()
        self.trader = trader
        self.trader.set_leverage(symbol, leverage)
        self.trade_ratio = trade_ratio
        self.asset = asset

    @abstractmethod
    def __call__(
        self,
        *candles: np.ndarray
    ): ...

    def get_quantity(self, signal: int, price: float):
        balance = self.trader.get_balance(self.asset)
        leverage = self.trader.get_leverage(self.symbol)

        return calculate_quantity(
            side=signal,
            balance=balance.total,
            leverage=leverage,
            price=price,
            trade_ratio=self.trade_ratio,
        )
