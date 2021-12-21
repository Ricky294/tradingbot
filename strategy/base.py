from abc import abstractmethod
from typing import Dict, Callable, List

import numpy as np
from crypto_data.binance.candle import StreamCandle
from crypto_data.binance.np.stream import candle_stream

from abstract import FuturesTrader, candles_with_trade_info

from model import SymbolTradeInfo, Balance


class Strategy(Callable):
    def __init__(self, symbol: str, trader: FuturesTrader):
        self.symbol = symbol.upper()
        self.trader = trader

    @abstractmethod
    def on_candle(
        self,
        candles: np.ndarray,
        symbol_trade_info: SymbolTradeInfo,
        balances: Dict[str, Balance],
    ):
        pass

    def __call__(
        self,
        candles: np.ndarray,
    ):
        candles_with_trade_info(
            symbol=self.symbol,
            trader=self.trader,
            candles=candles,
            callback=self.on_candle,
        )
