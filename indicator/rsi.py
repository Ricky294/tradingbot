import numpy as np
import pandas as pd
import talib

from crypto_data.binance.schema import CLOSE_PRICE

from consts.candle_column_index import COLUMN_NAME_INDEX_MAP
from indicator import Indicator
from util.numpy_util import cross_signal, Fit


class RSIIndicator(Indicator):
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

    def result(self, candles: np.ndarray):
        rsi = talib.RSI(candles.T[self.column_index], timeperiod=self.time_period)

        buy_signal_line = cross_signal(rsi, "<=", self.lower_limit, Fit.AFTER_LAST)
        sell_signal_line = cross_signal(rsi, ">=", self.upper_limit, Fit.AFTER_LAST)

        indicator_df = pd.DataFrame(
            {
                "rsi": rsi,
                "buy_signal": buy_signal_line,
                "sell_signal": sell_signal_line,
            }
        )
        return indicator_df
