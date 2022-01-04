from typing import Union

import numpy as np
import pandas as pd
from crypto_data.binance.schema import CLOSE_PRICE

from indicator import Indicator
from model.ma_type import MAType
from util.numpy_util import cross_signal, Fit
from util.trade import talib_ma


class MACrossIndicator(Indicator):
    @classmethod
    def sma(
        cls,
        fast_ma_period: int,
        slow_ma_period: int,
        fast_ma_column=CLOSE_PRICE,
        slow_ma_column=CLOSE_PRICE,
    ):
        return cls(
            fast_ma_type="SMA",
            slow_ma_type="SMA",
            fast_ma_period=fast_ma_period,
            slow_ma_period=slow_ma_period,
            fast_ma_column=fast_ma_column,
            slow_ma_column=slow_ma_column,
        )

    @classmethod
    def ema(
        cls,
        fast_ma_period: int,
        slow_ma_period: int,
        fast_ma_column=CLOSE_PRICE,
        slow_ma_column=CLOSE_PRICE,
    ):
        return cls(
            fast_ma_type="EMA",
            slow_ma_type="EMA",
            fast_ma_period=fast_ma_period,
            slow_ma_period=slow_ma_period,
            fast_ma_column=fast_ma_column,
            slow_ma_column=slow_ma_column,
        )

    @classmethod
    def wma(
        cls,
        fast_ma_period: int,
        slow_ma_period: int,
        fast_ma_column=CLOSE_PRICE,
        slow_ma_column=CLOSE_PRICE,
    ):
        return cls(
            fast_ma_type="WMA",
            slow_ma_type="WMA",
            fast_ma_period=fast_ma_period,
            slow_ma_period=slow_ma_period,
            fast_ma_column=fast_ma_column,
            slow_ma_column=slow_ma_column,
        )

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
        fast_ma_data = talib_ma(
            type=self.fast_ma_type,
            period=self.fast_ma_period,
            data=candles_T[self.fast_ma_column],
        )
        slow_ma_data = talib_ma(
            type=self.slow_ma_type,
            period=self.slow_ma_period,
            data=candles_T[self.fast_ma_column],
        )

        buy_signal = cross_signal(fast_ma_data, ">", slow_ma_data, Fit.FIRST)
        sell_signal = cross_signal(fast_ma_data, "<", slow_ma_data, Fit.FIRST)

        return pd.DataFrame({
            "fast": fast_ma_data,
            "slow": slow_ma_data,
            "buy_signal": buy_signal,
            "sell_signal": sell_signal,
        })
