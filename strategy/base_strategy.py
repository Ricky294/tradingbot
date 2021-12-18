from abc import abstractmethod
from typing import List, Dict, Callable

import pandas as pd
from crypto_data.binance.candle import StreamCandle

from abstract import FuturesTrader, candles_with_trade_info

from model import SymbolTradeInfo, Balance


class Strategy(Callable):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class SingleSymbolStrategy(Strategy):
    def __init__(self, symbol: str, trader: FuturesTrader):
        self.trader = trader
        self.symbol = symbol.upper()

    @abstractmethod
    def on_candle(
        self,
        candles: pd.DataFrame,
        symbol_trade_info: SymbolTradeInfo,
        balances: Dict[str, Balance],
    ):
        pass

    def __call__(
        self,
        candles: pd.DataFrame,
    ):
        candles_with_trade_info(
            symbol=self.symbol,
            trader=self.trader,
            candles=candles,
            callback=self.on_candle,
        )


class MultiSymbolStrategy(Strategy):
    def __init__(self, symbols: List[str], trader: FuturesTrader):
        self.trader = trader
        self.symbols = [symbol.upper() for symbol in symbols]

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
        from abstract import multi_candles_with_trade_info

        multi_candles_with_trade_info(
            candle=candle,
            symbols=self.symbols,
            trader=self.trader,
            candles=candles,
            callback=self.on_candle,
        )
