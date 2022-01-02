import numpy as np
import pandas as pd

from indicator import Indicator, RSIIndicator
from indicator.ma_trend import MATrendIndicator


class RSIWithMATrendIndicator(Indicator):

    def __init__(self, rsi: RSIIndicator, ma_trend: MATrendIndicator):
        self.rsi = rsi
        self.ma_trend = ma_trend

    def result(self, candles: np.ndarray) -> pd.DataFrame:
        rsi_result = self.rsi.result(candles)
        ma_trend_result = self.ma_trend.result(candles)

        buy_signal = ma_trend_result["buy_signal"] & rsi_result["buy_signal"]
        sell_signal = ma_trend_result["sell_signal"] & rsi_result["sell_signal"]

        return pd.DataFrame({
            "rsi": rsi_result["rsi"],
            "slow_ma": ma_trend_result["slow_ma"],
            "fast_ma": ma_trend_result["fast_ma"],
            "buy_signal": buy_signal,
            "sell_signal": sell_signal,
        })
