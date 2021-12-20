from typing import Callable, Dict

import numpy as np

from abstract import FuturesTrader
from model import Balance, SymbolTradeInfo


def candles_with_trade_info(
    symbol: str,
    trader: FuturesTrader,
    candles: np.ndarray,
    callback: Callable[[np.ndarray, SymbolTradeInfo, Dict[str, Balance]], any],
):
    from backtest import BacktestFuturesTrader

    if isinstance(trader, BacktestFuturesTrader):
        trader.__call__(candles)

    balances = trader.get_balances()
    position = trader.get_position(symbol=symbol)
    orders = trader.get_open_orders(symbol=symbol)
    symbol_info = trader.get_symbol_info(symbol=symbol)

    return callback(candles, SymbolTradeInfo(orders, symbol_info, position), balances)
