import numpy as np

from strategy import Strategy


def run_backtest(
    candles: np.ndarray,
    strategy: Strategy,
    skip: int = 0,
):
    from backtest import BacktestFuturesTrader
    if not isinstance(strategy.trader, BacktestFuturesTrader):
        raise ValueError("Trader is not an instance of BacktestFuturesTrader!")

    for i in range(skip, len(candles)):
        candles_head = candles[:i+1]
        strategy.trader(candles_head)
        strategy(candles_head)
