from typing import Dict

import pandas as pd

from strategy import SingleSymbolStrategy, MultiSymbolStrategy


def backtest_candle_multi_stream(
    symbol_candles_dict: Dict[str, pd.DataFrame],
    strategy: MultiSymbolStrategy,
    trader,
    skip: int = 0,
):
    symbols = tuple(symbol_candles_dict.keys())

    for i in range(skip, len(symbol_candles_dict)):
        candles_head = {
            symbol: symbol_candles_dict[symbol].head(i + 1) for symbol in symbols
        }

        trader(symbol_candles_dict)
        strategy(candle=None, candles=candles_head)


def backtest_candle_stream(
    candles: pd.DataFrame,
    strategy: SingleSymbolStrategy,
    trader,
    skip: int = 0,
    *args,
    **data,
):
    for i in range(skip, len(candles)):
        candles_head = candles.head(i + 1)
        trader(candles_head)
        strategy(candles_head)
