import numpy as np
import talib

from trader.core.const.candle_index import HIGH_PRICE_INDEX, LOW_PRICE_INDEX, CLOSE_PRICE_INDEX
from indicator.signal import Indicator


class DMIIndicator(Indicator):

    ADX_INDEX = 2
    PLUS_DI_INDEX = 3
    MINUS_DI_INDEX = 4

    def __init__(self, adx_period=14, plus_di_period=14, minus_di_period=14, adx_above=20):
        self.adx_period = adx_period
        self.plus_di_period = plus_di_period
        self.minus_di_period = minus_di_period

        self.adx_above = adx_above

    def __call__(self, candles: np.ndarray) -> np.ndarray:
        candles_T = candles.T
        adx = talib.ADX(
            candles_T[HIGH_PRICE_INDEX],
            candles_T[LOW_PRICE_INDEX],
            candles_T[CLOSE_PRICE_INDEX],
            self.adx_period
        )

        plus_di = talib.PLUS_DI(
            candles_T[HIGH_PRICE_INDEX],
            candles_T[LOW_PRICE_INDEX],
            candles_T[CLOSE_PRICE_INDEX],
            self.plus_di_period,
        )

        minus_di = talib.MINUS_DI(
            candles_T[HIGH_PRICE_INDEX],
            candles_T[LOW_PRICE_INDEX],
            candles_T[CLOSE_PRICE_INDEX],
            self.minus_di_period
        )

        buy_signal = (adx > self.adx_above) & (plus_di > minus_di)
        sell_signal = (adx > self.adx_above) & (plus_di < minus_di)

        return Indicator.concatenate_array(
            buy_signal,
            sell_signal,
            adx,
            plus_di,
            minus_di,
        )
