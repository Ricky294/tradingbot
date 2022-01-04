import numpy as np

from consts.trade_actions import BUY, SELL
from indicator import Indicator, RSIIndicator
from indicator.ma_trend import MATrendIndicator


class RSIWithMATrendIndicator(Indicator):

    RSI_INDEX = 2
    SLOW_MA_INDEX = 3
    FAST_MA_INDEX = 4

    def __init__(self, rsi: RSIIndicator, ma_trend: MATrendIndicator):
        self.rsi = rsi
        self.ma_trend = ma_trend

    def __call__(self, candles: np.ndarray):
        rsi_result = self.rsi(candles)
        ma_trend_result = self.ma_trend(candles)

        ma_buy_mask = ma_trend_result[BUY] == 1
        ma_sell_mask = ma_trend_result[SELL] == 1

        rsi_buy_mask = rsi_result[BUY] == 1
        rsi_sell_mask = rsi_result[SELL] == 1

        return np.concatenate((
            [ma_buy_mask & rsi_buy_mask],
            [ma_sell_mask & rsi_sell_mask],
            [rsi_result[RSIIndicator.RSI_INDEX]],
            [ma_trend_result[MATrendIndicator.SLOW_MA_INDEX]],
            [ma_trend_result[MATrendIndicator.FAST_MA_INDEX]],
        ))
