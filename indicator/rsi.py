import numpy as np
import talib

from crypto_data.binance.schema import CLOSE_PRICE

from consts.candle_index import COLUMN_NAME_INDEX_MAP
from indicator import Indicator
from util.numpy_util import cross_signal, Fit


class RSIIndicator(Indicator):

    RSI_INDEX = 2

    def __init__(
        self,
        column=CLOSE_PRICE,
        time_period=14,
        upper_limit=70,
        lower_limit=30,
    ):
        self.column_index = COLUMN_NAME_INDEX_MAP[column]
        self.time_period = time_period
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    def __call__(self, candles: np.ndarray):
        rsi = talib.RSI(candles.T[self.column_index], timeperiod=self.time_period)

        sell_signal_line = cross_signal(rsi, ">=", self.upper_limit, Fit.FIRST)
        buy_signal_line = cross_signal(rsi, "<=", self.lower_limit, Fit.FIRST)

        return np.concatenate((
            [buy_signal_line],
            [sell_signal_line],
            [rsi],
        ))
