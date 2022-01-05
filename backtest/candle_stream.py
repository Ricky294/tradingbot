import numpy as np
from tqdm import tqdm

from strategy import Strategy


def run_backtest(
    candles: np.ndarray,
    strategy: Strategy,
):
    from backtest import BacktestFuturesTrader
    if not isinstance(strategy.trader, BacktestFuturesTrader):
        raise ValueError("Trader is not an instance of BacktestFuturesTrader!")

    print(f"Backtesting on {len(candles)} candles.")
    for i in tqdm(range(len(candles))):
        candles_head = candles[:i+1]
        strategy(candles_head)
        strategy.trader(candles_head)

    print("Finished backtesting.")
