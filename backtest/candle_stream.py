import numpy as np

from strategy import Strategy


def backtest_candle_stream(
    candles: np.ndarray,
    strategy: Strategy,
    trader,
    skip: int = 0,
):
    for i in range(skip, len(candles)):
        candles_head = candles[:i+1]
        trader(candles_head)
        strategy(candles_head)
