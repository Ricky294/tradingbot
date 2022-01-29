from typing import Tuple

import numpy as np

from trader.core.const.candle_index import CLOSE_PRICE_INDEX
from trader.core.const.trade_actions import BUY
from indicator.sltp import SLTPIndicator


class RelativeToPrice(SLTPIndicator):

    def __init__(self, sl_multiple: float, tp_multiple: float):
        if sl_multiple >= 1 or sl_multiple <= 0:
            raise ValueError("Parameter sl_multiple must be between 0 and 1")
        if tp_multiple <= 1:
            raise ValueError("Parameter tp_multiple must be greater than 1")

        self.sl_multiple = sl_multiple
        self.tp_multiple = tp_multiple

    def __call__(self, candles: np.ndarray, side: int, leverage: int) -> Tuple[float, float]:
        latest_close = float(candles[-1][CLOSE_PRICE_INDEX])

        if side == BUY:
            return latest_close * self.sl_multiple, latest_close * self.tp_multiple
        return latest_close * self.tp_multiple, latest_close * self.sl_multiple
