from typing import Dict

import pandas as pd

from strategy import SingleSymbolStrategy, MultiSymbolStrategy


def backtest_candle_multi_stream(
    candles: Dict[str, pd.DataFrame],
    strategy: MultiSymbolStrategy,
    trader,
    skip: int = 0,
):
    """
    Simulates continuous data creation.
    """

    for i in range(skip, len(candles)):
        candles_head = candles.head(i + 1)
        trader({strategy.symbols})
        strategy(candles_head)


def backtest_candle_stream(
    candles: pd.DataFrame,
    strategy: SingleSymbolStrategy,
    trader,
    skip: int = 0,
    *args,
    **kwargs,
):
    """
    Simulates continuous data creation.
    """
    for i in range(skip, len(candles)):
        candles_head = candles.head(i + 1)
        trader({strategy.symbol: candles_head})
        strategy(candles_head)
