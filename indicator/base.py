from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class Indicator(ABC):
    @abstractmethod
    def __init__(self, *args, **data):
        pass

    @abstractmethod
    def result(self, candles: np.ndarray) -> pd.DataFrame:
        pass
