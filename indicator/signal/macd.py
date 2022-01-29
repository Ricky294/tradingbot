import numpy as np

from trader.core.const.candle_index import CLOSE_PRICE_INDEX
from trader.core.util.np import cross_signal, Fit
import talib


from indicator.signal import Indicator


class MACDIndicator(Indicator):

    MACD_INDEX = 2
    SIGNAL_INDEX = 3
    HISTOGRAM_INDEX = 4

    def __init__(
        self,
        column_index=CLOSE_PRICE_INDEX,
        fast_period=12,
        slow_period=26,
        signal_period=9,
    ):
        self.column_index = column_index
        self.fast_period = fast_period      # macd line
        self.slow_period = slow_period      # signal line
        self.signal_period = signal_period

    def __call__(self, candles: np.ndarray):
        macd, signal, histogram = talib.MACD(
            candles.T[self.column_index],
            fastperiod=self.fast_period,
            slowperiod=self.slow_period,
            signalperiod=self.signal_period
        )

        sell_signal = cross_signal(macd, "<", signal, Fit.FIRST)
        buy_signal = cross_signal(macd, ">", signal, Fit.FIRST)

        return Indicator.concatenate_array(
            buy_signal,
            sell_signal,
            macd,
            signal,
            histogram,
        )

