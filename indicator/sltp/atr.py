from typing import Tuple

import numpy as np
import talib

from trader.core.const.candle_index import CLOSE_PRICE_INDEX, HIGH_PRICE_INDEX, LOW_PRICE_INDEX
from trader.core.const.trade_actions import BUY, SELL

from indicator.sltp import SLTPIndicator


class ATRIndicator(SLTPIndicator):
    def __init__(self, time_period=14):
        self.time_period = time_period

    def __call__(self, candles: np.ndarray, side: int, leverage: int) -> Tuple[float, float]:
        candles_T = candles.T

        atr = talib.ATR(
            candles_T[HIGH_PRICE_INDEX],
            candles_T[LOW_PRICE_INDEX],
            candles_T[CLOSE_PRICE_INDEX],
            timeperiod=self.time_period,
        )

        latest_close_price = float(candles[-1][CLOSE_PRICE_INDEX])
        latest_atr = float(atr[-1])

        if side == BUY:
            return latest_close_price - latest_atr, latest_close_price + latest_atr
        elif side == SELL:
            return latest_close_price + latest_atr, latest_close_price - latest_atr
