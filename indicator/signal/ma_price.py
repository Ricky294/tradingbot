from typing import Union

import numpy as np

from trader.core.const.candle_index import CLOSE_PRICE_INDEX
from indicator.signal import Indicator
from trader.core.enum import MAType
from util.trade import talib_ma


class MAPriceIndicator(Indicator):

    MA_INDEX = 2

    def __init__(
            self,
            ma_period: int,
            ma_type: Union[str, MAType],
            ma_column_index: int,
    ):
        self.ma_period = ma_period
        self.ma_type = str(ma_type)
        self.ma_column_index = ma_column_index

    def __call__(self, candles: np.ndarray):
        candles_T = candles.T

        ma = talib_ma(
            type=self.ma_type,
            period=self.ma_period,
            data=candles_T[self.ma_column_index],
        )

        close_price_series = candles_T[CLOSE_PRICE_INDEX]

        buy_signal = ma < close_price_series
        sell_signal = ma > close_price_series

        return Indicator.concatenate_array(
            buy_signal,
            sell_signal,
            ma,
        )

