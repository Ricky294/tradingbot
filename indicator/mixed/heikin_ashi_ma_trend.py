import numpy as np

from consts.trade_actions import BUY, SELL
from indicator import Indicator
from indicator.heikin_ashi import HeikinAshiIndicator
from indicator.ma_trend import MATrendIndicator


class HeikinAshiMATrendIndicator(Indicator):
    def __init__(self, ha: HeikinAshiIndicator, ma_trend: MATrendIndicator):
        self.ha = ha
        self.ma_trend = ma_trend

    def __call__(self, candles: np.ndarray) -> np.ndarray:
        ha_result = self.ha(candles)
        ma_trend_result = self.ma_trend(candles)

        ha_buy_mask = ha_result[BUY] == 1
        ha_sell_mask = ha_result[SELL] == 1

        ma_buy_mask = ma_trend_result[BUY] == 1
        ma_sell_mask = ma_trend_result[SELL] == 1

        return np.concatenate((
            [ma_buy_mask & ha_buy_mask],
            [ma_sell_mask & ha_sell_mask],
        ))
