import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def create_plots(
        open_time: np.ndarray,
        close_prices: np.ndarray,
        capital: np.ndarray,
        volume: np.ndarray,
        entry_time: np.ndarray,
        exit_time: np.ndarray,
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

    axis2.plot(open_time, close_prices, label="Close price")
    axis2.scatter(entry_time, close_prices * 0.9, s=20, color="green", marker="^", label="Entries")
    axis2.scatter(exit_time, close_prices * 1.1, s=20, color="red", marker="v", label="Exits")
    axis2.legend()

    axis3.plot(open_time, volume, label="Volume")
    axis3.legend()

    return fig
