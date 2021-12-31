import numpy as np
import pandas as pd

from consts.candle_column_index import CLOSE_PRICE_INDEX
from util.numpy_util import cross_signal
import talib


from indicator import Indicator


class MACDIndicator(Indicator):
    def __init__(
        self,
        column=CLOSE_PRICE_INDEX,
        fast_period=12,
        slow_period=26,
        signal_period=9,
    ):
        self.column = column
        self.fast_period = fast_period      # macd line
        self.slow_period = slow_period      # signal line
        self.signal_period = signal_period

    def result(self, candles: np.ndarray):
        macd, signal, histogram = talib.MACD(
            candles.T[self.column],
            fastperiod=self.fast_period,
            slowperiod=self.slow_period,
            signalperiod=self.signal_period
        )

        sell_signal = cross_signal(macd, "<", signal)
        buy_signal = cross_signal(macd, ">", signal)

        indicator_df = pd.DataFrame(
            {"macd": macd, "signal": signal, "histogram": histogram, "buy_signal": buy_signal, "sell_signal": sell_signal}
        )
        return indicator_df
