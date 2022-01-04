from typing import Union

import numpy as np

from indicator import Indicator
from model.ma_type import MAType
from util.trade import talib_ma


class MATrendIndicator(Indicator):

    SLOW_MA_INDEX = 2
    FAST_MA_INDEX = 3

    def __init__(
            self,
            slow_period: int,
            slow_type: Union[str, MAType],
            slow_column_index: int,
            fast_period: int,
            fast_type: Union[str, MAType],
            fast_column_index: int,
    ):
        self.slow_period = slow_period
        self.slow_type = str(slow_type)
        self.slow_column_index = slow_column_index

        self.fast_period = fast_period
        self.fast_type = str(fast_type)
        self.fast_column_index = fast_column_index

    def __call__(self, candles: np.ndarray):
        candles_T = candles.T

        slow_ma = talib_ma(
            type=self.slow_type,
            period=self.slow_period,
            data=candles_T[self.slow_column_index],
        )
        fast_ma = talib_ma(
            type=self.fast_type,
            period=self.fast_period,
            data=candles_T[self.fast_column_index],
        )

        buy_signal = fast_ma > slow_ma
        sell_signal = fast_ma < slow_ma

        return np.concatenate((
            [buy_signal],
            [sell_signal],
            [slow_ma],
            [fast_ma],
        ))