import pandas as pd

from typing import List

from indicator import RSIIndicator
from model import Balance, SymbolTradeInfo
from strategy import SingleSymbolStrategy
from abstract import FuturesTrader


class RSIStrategy(SingleSymbolStrategy):
    def __init__(self, symbol: str, trader: FuturesTrader, rsi: RSIIndicator):
        super().__init__(symbol=symbol, trader=trader)
        self.rsi = rsi

    def on_candle(
        self,
        candles: pd.DataFrame,
        trade_info: SymbolTradeInfo,
        balances: List[Balance],
    ):
        result = self.rsi.result(candles)
        self.trader.create_orders()
