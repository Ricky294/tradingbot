import numpy as np
import talib


def talib_ma(type: str, period: int, data: np.ndarray) -> np.ndarray:
    return getattr(talib, type)(data, timeperiod=period)
