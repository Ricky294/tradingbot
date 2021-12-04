from abc import ABC, abstractmethod

import pandas as pd


class Indicator(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def result(self, candle_df: pd.DataFrame) -> pd.DataFrame:
        pass
