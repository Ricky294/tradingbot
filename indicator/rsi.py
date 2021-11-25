import pandas as pd
import talib
from crypto_data.binance.schema import CLOSE_PRICE

from indicator.indicator import Indicator


class RSI(Indicator):
    def __init__(
        self,
        df: pd.DataFrame,
        column: str = CLOSE_PRICE,
        time_period: int = 14,
        upper_limit=70,
        lower_limit=30,
    ):
        self.rsi = talib.RSI(df[column].values, timeperiod=time_period)
        self.time_period = time_period
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    def buy_signal(self) -> bool:
        return self.rsi[-1] < self.lower_limit

    def sell_signal(self) -> bool:
        return self.rsi[-1] > self.upper_limit

    def __str__(self):
        return f"RSI: {self.rsi[-1]}, Time period: {self.time_period} Upper limit: {self.upper_limit}, Lower limit: {self.lower_limit}"
