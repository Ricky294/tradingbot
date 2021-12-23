import pandas as pd
try:
    import talib
except ImportError:
    print("Could not find talib package.")
from crypto_data.binance.schema import HIGH_PRICE, LOW_PRICE, CLOSE_PRICE

from indicator import Indicator


class ATRIndicator(Indicator):
    def __init__(self, time_period=14, slow_period=30, fast_period=3):
        self.time_period = time_period
        self.slow_period = slow_period
        self.fast_period = fast_period

    def result(self, candle_df: pd.DataFrame) -> pd.DataFrame:
        atr = talib.ATR(
            candle_df[HIGH_PRICE],
            candle_df[LOW_PRICE],
            candle_df[CLOSE_PRICE],
            timeperiod=self.time_period,
        )
        indicator_df = pd.DataFrame(atr, columns=["ATR"])
        return indicator_df
