from typing import Callable, List, Dict

import pandas as pd
from binance.client import Client
from crypto_data.binance.candle import StreamCandle

from binance_.futures import (
    get_futures_position,
    get_futures_open_orders,
    get_futures_symbol_info,
    get_futures_balances,
)
from model import Balance, SymbolTradeInfo


def multi_candles_with_trade_info(
    symbols: List[str],
    candle: StreamCandle,
    client: Client,
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
    balances = get_futures_balances(client)
    symbol_trade_info = {
        symbol.upper(): SymbolTradeInfo(
            orders=get_futures_open_orders(client, symbol=symbol),
            symbol_info=get_futures_symbol_info(client, symbol=symbol),
            position=get_futures_position(client, symbol=symbol),
        )
        for symbol in symbols
    }

    return callback(candle, candles, symbol_trade_info, balances)


def candles_with_trade_info(
    symbol: str,
    client: Client,
    candles: pd.DataFrame,
    callback: Callable[[pd.DataFrame, SymbolTradeInfo, List[Balance]], any],
):
    balances = get_futures_balances(client)
    position = get_futures_position(client, symbol=symbol)
    orders = get_futures_open_orders(client, symbol=symbol)
    symbol_info = get_futures_symbol_info(client, symbol=symbol)

    return callback(candles, SymbolTradeInfo(orders, symbol_info, position), balances)
