import pandas as pd
import talib
from crypto_data.binance.schema import CLOSE_PRICE

from indicator import Indicator, IndicatorResult


class MACDIndicator(Indicator):
    def __init__(
        self,
        column=CLOSE_PRICE,
        fast_period=12,
        slow_limit=26,
        signal_period=9,
    ):
        self.column = column
        self.fast_period = fast_period
        self.slow_limit = slow_limit
        self.signal_period = signal_period

    def result(self, candle_df: pd.DataFrame):
        macd, signal, histogram = talib.MACD(
            candle_df[self.column], fastperiod=12, slowperiod=26, signalperiod=9
        )

        indicator_df = pd.DataFrame(
            {"macd": macd, "signal": signal, "histogram": histogram}
        )
        return IndicatorResult(
            dataframe=indicator_df,
            buy_signal=(macd[-1] > signal[-1]) and (macd[-2] < signal[-2]),
            sell_signal=(macd[-1] < signal[-1]) and (macd[-2] > signal[-2]),
        )
