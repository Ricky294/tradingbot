import numpy as np
import pandas as pd
import talib
from crypto_data.binance.schema import CLOSE_PRICE

from indicator import Indicator, IndicatorResult
from numpy_util import cross_signal


class RSIIndicator(Indicator):
    def __init__(
        self,
        column=CLOSE_PRICE,
        time_period=14,
        upper_limit=70,
        lower_limit=30,
    ):
        self.column = column
        self.time_period = time_period
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    def result(self, candle_df: pd.DataFrame):
        rsi = talib.RSI(candle_df[self.column].values, timeperiod=self.time_period)
        buy_signal_line = cross_signal(rsi, ">=", self.lower_limit)
        sell_signal_line = cross_signal(rsi, "<=", self.upper_limit)

        indicator_df = pd.DataFrame(
            {
                "rsi": rsi,
                "buy_signal": buy_signal_line,
                "sell_signal": sell_signal_line,
            }
        )
        return IndicatorResult(
            dataframe=indicator_df,
            buy_signal=rsi[-1] <= self.lower_limit,
            sell_signal=rsi[-1] >= self.upper_limit,
        )


x = np.array([5, 10, 20, 30.2, 40, 32, 5])
y = np.array([1, 2, 3, 35, 55, 20, 10])

z = np.array((x > 30) & (x[-1] < 30))
