from abc import abstractmethod
from typing import List, Dict, Callable

import pandas as pd
from crypto_data.binance.candle import StreamCandle

from binance_.trade_info_provider import (
    candles_with_trade_info,
    multi_candles_with_trade_info,
)
from model import SymbolTradeInfo, Balance
from trader import Trader


class Strategy(Callable):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class SingleSymbolStrategy(Strategy):
    def __init__(self, symbol: str, trader: Trader):
        self.trader = trader
        self.symbol = symbol

    @abstractmethod
    def on_candle(
        self,
        candles: pd.DataFrame,
        symbol_trade_info: SymbolTradeInfo,
        balances: List[Balance],
    ):
        pass

    def __call__(
        self,
        candles: pd.DataFrame,
    ):
        candles_with_trade_info(
            symbol=self.symbol,
            client=self.trader.client,
            candles=candles,
            callback=self.on_candle,
        )


class MultiSymbolStrategy(Strategy):
    def __init__(self, symbols: List[str], trader: Trader):
        self.trader = trader
        self.symbols = symbols

    @abstractmethod
    def on_candle(
        self,
        candle: StreamCandle,
        candles: Dict[str, pd.DataFrame],
        symbol_trade_info: Dict[str, SymbolTradeInfo],
        balances: List[Balance],
    ):
        pass

    def __call__(self, candle: StreamCandle, candles: Dict[str, pd.DataFrame]):
        multi_candles_with_trade_info(
            candle=candle,
            symbols=self.symbols,
            client=self.trader.client,
            candles=candles,
            callback=self.on_candle,
        )