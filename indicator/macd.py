import pandas as pd
try:
    import talib
except ImportError:
    print("Could not find talib package.")
from crypto_data.binance.schema import CLOSE_PRICE

from indicator import Indicator


class MACDIndicator(Indicator):
    def __init__(
        self,
        column=CLOSE_PRICE,
        fast_period=12,
        slow_period=26,
        signal_period=9,
    ):
        self.column = column
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def result(self, candle_df: pd.DataFrame):
        macd, signal, histogram = talib.MACD(
            candle_df[self.column],
            fastperiod=self.fast_period,
            slowperiod=self.slow_period,
            signalperiod=self.signal_period
        )

        indicator_df = pd.DataFrame(
            {"macd": macd, "signal": signal, "histogram": histogram}
        )
        return indicator_df
