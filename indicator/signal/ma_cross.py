from typing import Union

import numpy as np
from crypto_data.binance.schema import CLOSE_PRICE

from indicator.signal import Indicator
from trader.core.enum import MAType
from trader.core.util.np import cross_signal, Fit
from util.trade import talib_ma


class MACrossIndicator(Indicator):

    SLOW_MA_INDEX = 2
    FAST_MA_INDEX = 3

    def __init__(
        self,
        fast_ma_period: int,
        fast_ma_type: Union[str, MAType],
        slow_ma_period: int,
        slow_ma_type: Union[str, MAType],
        fast_ma_column=CLOSE_PRICE,
        slow_ma_column=CLOSE_PRICE,
    ):
        self.fast_ma_period = fast_ma_period
        self.fast_ma_type = fast_ma_type
        self.fast_ma_column = fast_ma_column

        self.slow_ma_period = slow_ma_period
        self.slow_ma_type = slow_ma_type
        self.slow_ma_column = slow_ma_column

    def __call__(self, candles: np.ndarray):
        candles_T = candles.T
        fast_ma = talib_ma(
            type=self.fast_ma_type,
            period=self.fast_ma_period,
            data=candles_T[self.fast_ma_column],
        )
        slow_ma = talib_ma(
            type=self.slow_ma_type,
            period=self.slow_ma_period,
            data=candles_T[self.fast_ma_column],
        )

        buy_signal = cross_signal(fast_ma, ">", slow_ma, Fit.FIRST)
        sell_signal = cross_signal(fast_ma, "<", slow_ma, Fit.FIRST)

        return Indicator.concatenate_array(
            buy_signal,
            sell_signal,
            slow_ma,
            fast_ma,
        )
