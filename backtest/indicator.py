import numpy as np

from indicator import Indicator


class BacktestIndicator(Indicator):
    def __init__(self, candles: np.ndarray, indicator: Indicator, skip=0):
        self.indicator = indicator
        self.indicator_data = indicator.result(candles)
        self.skip = skip
        self.index = skip

    def result(self, *args, **data):
        self.index = self.index + 1
        indicator_data_head = self.indicator_data[:self.index]
        return indicator_data_head
