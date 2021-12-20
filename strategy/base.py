from abc import abstractmethod
from typing import List, Dict, Callable

import numpy as np
import pandas as pd
from crypto_data.binance.candle import StreamCandle
from crypto_data.binance.stream import candle_stream

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

    def run_backtest(self, candles: np.ndarray, skip=0):
        from backtest import backtest_candle_stream
        backtest_candle_stream(
            candles=candles,
            strategy=self,
            trader=self.trader,
            skip=skip,
        )

    def run_live(
            self,
            interval: str,
            market: str,
            candles: np.ndarray,
            on_candle: Callable[[StreamCandle], any],
            on_candle_close: Callable[[np.ndarray], any]
    ):
        candle_stream(
            symbol=self.symbol,
            interval=interval,
            market=market,
            candles=candles,
            on_candle=on_candle,
            on_candle_close=on_candle_close,
        )
