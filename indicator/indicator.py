from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd

from model.order import OrderSide


class Indicator(ABC):
    @abstractmethod
    def __init__(self, df: pd.DataFrame):
        pass

    def signal_enum(self) -> Optional[OrderSide]:
        if self.buy_signal():
            return OrderSide.BUY
        elif self.sell_signal():
            return OrderSide.SELL

    def signal(self) -> Optional[str]:
        if self.buy_signal():
            return "BUY"
        elif self.sell_signal():
            return "SELL"

    @abstractmethod
    def buy_signal(self) -> bool:
        pass

    @abstractmethod
    def sell_signal(self) -> bool:
        pass
