from typing import Callable

import pandas as pd


def backtest_candle_stream(
    candles: pd.DataFrame,
    on_candle_close: Callable[[pd.DataFrame], None],
    skip: int = 0,
    *args,
    **kwargs,
):
    """
    Simulates continuous data creation.
    """
    for i in range(skip, len(candles)):
        candles_head = candles.head(i + 1)
        on_candle_close(candles_head)
