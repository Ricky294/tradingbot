import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from backtest import BacktestFuturesTrader
from consts.candle_column_index import (
    OPEN_TIME_INDEX,
    CLOSE_PRICE_INDEX,
    VOLUME_INDEX,
)
from plot.transform import extend_data


def create_plots(
        open_time: np.ndarray,
        close_price: np.ndarray,
        capital: np.ndarray,
        volume: np.ndarray,
        entry_time: np.ndarray,
        exit_time: np.ndarray,
        **kwargs,
):
    axis1: Axes
    axis2: Axes
    axis3: Axes
    fig: Figure

    fig, (axis1, axis2, axis3) = plt.subplots(
        3, 1, sharex=True,  # ignore warning
        gridspec_kw={"hspace": 0.0, "height_ratios": [0.9, 2, 0.9]}
    )

    open_time = pd.to_datetime(open_time, unit="s")
    entry_time = pd.to_datetime(entry_time, unit="s")
    exit_time = pd.to_datetime(exit_time, unit="s")

    axis1.plot(open_time, capital, label="Capital")
    axis1.legend()
    axis1.text(x=open_time[-1], y=capital[-1], s=str(int(capital[-1])), fontsize=10)

    axis2.plot(open_time, close_price, label="Close price")
    axis2.scatter(entry_time, close_price * 0.9, s=20, color="green", marker="^", label="Entries")
    axis2.scatter(exit_time, close_price * 1.1, s=20, color="red", marker="v", label="Exits")
    axis2.legend()

    axis3.plot(open_time, volume, label="Volume")
    axis3.legend()


def plot_backtest_results(
        candles: np.ndarray,
        trader: BacktestFuturesTrader,
):
    positions = trader.positions

    candles_T = candles.T
    extended_data = extend_data(
        open_time=candles_T[OPEN_TIME_INDEX],
        entry_time=np.array(tuple(position.time for position in positions)),
        entry_price=np.array(tuple(position.price for position in positions)),
        exit_time=np.array(tuple(position.exit_time for position in positions)),
        exit_price=np.array(tuple(position.exit_price for position in positions)),
        profit=np.array(tuple(position.exit_profit for position in positions)),
        quantity=np.array(tuple(position.quantity for position in positions)),
        side=np.array(tuple(position.side for position in positions)),
        starting_capital=trader.initial_balance.balance,
    )

    create_plots(
        open_time=candles_T[OPEN_TIME_INDEX],
        close_price=candles_T[CLOSE_PRICE_INDEX],
        volume=candles_T[VOLUME_INDEX],
        **extended_data,
    )

    plt.show()
