from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd

from model import OrderSide


class IndicatorResult:
    def __init__(
        self,
        dataframe: pd.DataFrame,
        buy_signal: bool,
        sell_signal: bool,
    ):
        self.dataframe = dataframe
        self.buy_signal = buy_signal
        self.sell_signal = sell_signal

    @property
    def signal(self) -> Optional[str]:
        if self.buy_signal:
            return "BUY"
        elif self.sell_signal:
            return "SELL"

    @property
    def side(self) -> Optional[OrderSide]:
        if self.buy_signal:
            return OrderSide.BUY
        elif self.sell_signal:
            return OrderSide.SELL


class Indicator(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def result(self, candle_df: pd.DataFrame) -> IndicatorResult:
        pass
