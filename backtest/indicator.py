import numpy as np

from indicator import Indicator


class BacktestIndicator(Indicator):
    def __init__(self, candles: np.ndarray, indicator: Indicator, skip=0):
        self.indicator = indicator
        self.__result = indicator(candles).T
        self.__skip = skip
        self.__index = skip

    def __call__(self, *args, **data):
        self.__index = self.__index + 1
        next_data = self.__result[:self.__index]
        return next_data

    @property
    def index(self):
        return self.__index
