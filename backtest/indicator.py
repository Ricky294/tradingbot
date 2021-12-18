import pandas as pd
from indicator import Indicator


class BacktestIndicator(Indicator):
    def __init__(self, indicator: Indicator, candle_df: pd.DataFrame, skip=0):
        self.indicator = indicator
        self.indicator_df = indicator.result(candle_df)
        self.index = skip

    def result(self, *args, **data):
        self.index = self.index + 1
        indicator_df_head = self.indicator_df.head(self.index)
        return indicator_df_head
