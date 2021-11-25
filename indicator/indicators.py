from enum import Enum
from typing import Union

from indicator.indicator import Indicator


class SignalMode(Enum):
    ANY = "ANY"
    ALL = "ALL"


class Indicators(Indicator):
    def __init__(self, signal_mode: Union[SignalMode, str], *indicators: Indicator):
        self.signal_mode = str(signal_mode).lower()
        self.indicators = indicators

    def buy_signal(self) -> bool:
        return getattr(globals()["__builtins__"], self.signal_mode)(
            ind.buy_signal() for ind in self.indicators
        )

    def sell_signal(self) -> bool:
        return getattr(globals()["__builtins__"], self.signal_mode)(
            ind.sell_signal() for ind in self.indicators
        )
