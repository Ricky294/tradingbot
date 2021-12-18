import pandas as pd
from crypto_data.binance.schema import (
    OPEN_TIME,
    OPEN_PRICE,
    CLOSE_PRICE,
    LOW_PRICE,
    HIGH_PRICE,
    VOLUME,
)


class Candle:

    __slots__ = (OPEN_TIME, OPEN_PRICE, CLOSE_PRICE, LOW_PRICE, HIGH_PRICE, VOLUME)

    def __init__(
        self,
        open_time: int,
        open_price: float,
        close_price: float,
        low_price: float,
        high_price: float,
        volume: float,
    ):
        self.open_time = open_time
        self.open_price = open_price
        self.close_price = close_price
        self.low_price = low_price
        self.high_price = high_price
        self.volume = volume

    @classmethod
    def from_dataframe(cls, candle: pd.DataFrame):
        return cls(
            open_time=candle[OPEN_TIME].item(),
            open_price=candle[OPEN_PRICE].item(),
            close_price=candle[CLOSE_PRICE].item(),
            low_price=candle[LOW_PRICE].item(),
            high_price=candle[HIGH_PRICE].item(),
            volume=candle[VOLUME].item(),
        )
