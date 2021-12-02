from enum import Enum
from typing import Union

import numpy as np
import pandas as pd
import talib
from crypto_data.binance.schema import CLOSE_PRICE

from indicator import Indicator, IndicatorResult
from numpy_util import cross_signal


class MAType(Enum):
    EMA = "EMA"
    WMA = "WMA"
    SMA = "SMA"


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

    def result(self, candle_df: pd.DataFrame) -> IndicatorResult:
        def talib_ma(ma_type: str, ma_column: str, ma_period: int) -> np.ndarray:
            return getattr(talib, ma_type)(candle_df[ma_column], timeperiod=ma_period)

        fast_ma_data = talib_ma(
            self.fast_ma_type, self.fast_ma_column, self.fast_ma_period
        )
        slow_ma_data = talib_ma(
            self.slow_ma_type, self.slow_ma_column, self.slow_ma_period
        )

        buy_signal_line = cross_signal(fast_ma_data, ">", slow_ma_data)
        sell_signal_line = cross_signal(fast_ma_data, "<", slow_ma_data)

        return IndicatorResult(
            dataframe=pd.DataFrame(
                {
                    "fast": fast_ma_data,
                    "slow": slow_ma_data,
                    "buy_signal": buy_signal_line,
                    "sell_signal": sell_signal_line,
                }
            ),
            buy_signal=(fast_ma_data[-1] > slow_ma_data[-1])
            and (fast_ma_data[-2] < slow_ma_data[-2]),
            sell_signal=(fast_ma_data[-1] < slow_ma_data[-1])
            and (fast_ma_data[-2] > slow_ma_data[-2]),
        )
