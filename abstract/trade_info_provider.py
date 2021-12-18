from typing import Callable, List, Dict

import pandas as pd
from crypto_data.binance.candle import StreamCandle

from abstract import FuturesTrader

from model import Balance, SymbolTradeInfo


def multi_candles_with_trade_info(
    symbols: List[str],
    candle: StreamCandle,
    trader: FuturesTrader,
    candles: Dict[str, pd.DataFrame],
    callback: Callable[
        [
            StreamCandle,
            Dict[str, pd.DataFrame],
            Dict[str, SymbolTradeInfo],
            List[Balance],
        ],
        any,
    ],
):
    from backtest import BacktestFuturesTrader

    if isinstance(trader, BacktestFuturesTrader):
        trader.__call__(candles)

    balances = trader.get_balances()
    symbol_trade_info = {
        symbol.upper(): SymbolTradeInfo(
            position=trader.get_position(symbol=symbol),
            orders=trader.get_open_orders(symbol=symbol),
            symbol_info=trader.get_symbol_info(symbol=symbol),
        )
        for symbol in symbols
    }

    return callback(candle, candles, symbol_trade_info, balances)


def candles_with_trade_info(
    symbol: str,
    trader: FuturesTrader,
    candles: pd.DataFrame,
    callback: Callable[[pd.DataFrame, SymbolTradeInfo, Dict[str, Balance]], any],
):
    from backtest import BacktestFuturesTrader

    if isinstance(trader, BacktestFuturesTrader):
        trader.__call__(candles)

    balances = trader.get_balances()
    position = trader.get_position(symbol=symbol)
    orders = trader.get_open_orders(symbol=symbol)
    symbol_info = trader.get_symbol_info(symbol=symbol)

    return callback(candles, SymbolTradeInfo(orders, symbol_info, position), balances)
