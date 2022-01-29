import numpy as np

from trader.core.const.candle_index import OPEN_PRICE_INDEX, HIGH_PRICE_INDEX, LOW_PRICE_INDEX, CLOSE_PRICE_INDEX
from trader.core.util.trade import to_heikin_ashi

from indicator.signal import Indicator


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

            return Indicator.concatenate_array(buy_signal_line=buy_signal, sell_signal_line=sell_signal)

        buy_signal = ha_close > ha_open
        sell_signal = ha_close < ha_open
        return Indicator.concatenate_array(buy_signal_line=buy_signal, sell_signal_line=sell_signal)