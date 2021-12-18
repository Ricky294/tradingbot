import pandas as pd
from matplotlib import pyplot as plt


def plot_trade_result(df: pd.DataFrame):
    figure, (axis1, axis2) = plt.subplots(
        2, 1, sharex=True, gridspec_kw={"hspace": 0.0, "height_ratios": [1, 2]}
    )

    time_series = pd.to_datetime(df["time"], unit="s")

    axis1.plot(time_series, df["capital"].fillna(method="ffill"))
    axis2.plot(time_series, df["close_price"].values)
    plt.show()
