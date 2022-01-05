import numpy as np

from consts.candle_index import OPEN_PRICE_INDEX, HIGH_PRICE_INDEX, LOW_PRICE_INDEX, CLOSE_PRICE_INDEX
from indicator import Indicator
from util.trade import to_heikin_ashi


class HeikinAshiIndicator(Indicator):
    def __init__(self, strong_only=True):
        self.strong_only = strong_only

    def __call__(self, candles: np.ndarray) -> np.ndarray:
        candles_T = candles.T

        ha_open, ha_high, ha_low, ha_close = to_heikin_ashi(
            open=candles_T[OPEN_PRICE_INDEX],
            high=candles_T[HIGH_PRICE_INDEX],
            low=candles_T[LOW_PRICE_INDEX],
            close=candles_T[CLOSE_PRICE_INDEX],
        )

        if self.strong_only:
            buy_signal = ha_open == ha_low
            sell_signal = ha_open == ha_high

            return np.concatenate((
                [buy_signal],
                [sell_signal],
            ))

        buy_signal = ha_close > ha_open
        sell_signal = ha_close < ha_open
        return np.concatenate((
            [buy_signal],
            [sell_signal],
        ))
