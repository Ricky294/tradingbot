import numpy as np
import pandas as pd

import dash
from dash import dcc
from dash import html

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backtest import (
    TIME_INDEX,
    PRICE_INDEX,
    QUANTITY_INDEX,
    EXIT_TIME_INDEX,
    EXIT_PRICE_INDEX, SIDE_INDEX, PROFIT_INDEX, EXIT_QUANTITY_INDEX
)
from consts.candle_column_index import (
    OPEN_TIME_INDEX,
    OPEN_PRICE_INDEX,
    HIGH_PRICE_INDEX,
    LOW_PRICE_INDEX,
    CLOSE_PRICE_INDEX,
    VOLUME_INDEX,
)
from plot.transform import assign_where_not_zero
from util.numpy import map_match


def __create_custom_data(*arrays: np.ndarray):
    return np.stack(tuple(arrays), axis=-1)


def create_plots(
        candles: np.ndarray,
        entry_time: np.ndarray,
        entry_price: np.ndarray,
        entry_quantity: np.ndarray,
        entry_side: np.ndarray,
        middle_time: np.ndarray,
        middle_price: np.ndarray,
        middle_quantity: np.ndarray,
        exit_time: np.ndarray,
        exit_price: np.ndarray,
        exit_quantity: np.ndarray,
        profit: np.ndarray,
        capital: np.ndarray,
        candlestick_plot=True,
        volume_bar_plot=True,
):
    high_price = candles[HIGH_PRICE_INDEX]
    low_price = candles[LOW_PRICE_INDEX]
    open_time = candles[OPEN_TIME_INDEX]
    close_price = candles[CLOSE_PRICE_INDEX]
    volume = candles[VOLUME_INDEX]

    if candlestick_plot and (high_price is None or low_price is None):
        raise ValueError("high_price and low_price parameter is required if candlestick_plot is True")

    open_time = pd.to_datetime(open_time, unit="s")
    entry_time = pd.to_datetime(entry_time, unit="s")
    middle_time = pd.to_datetime(middle_time, unit="s")
    exit_time = pd.to_datetime(exit_time, unit="s")

    candlestick_plot_type = "candlestick" if candlestick_plot else "scatter"
    volume_bar_plot_type = "bar" if volume_bar_plot else "scatter"

    fig = make_subplots(
        rows=3, cols=1,
        column_widths=[1.0],
        row_heights=[0.2, 0.6, 0.2],
        shared_xaxes=True,
        horizontal_spacing=0.0,
        vertical_spacing=0.02,
        specs=[
            [{"type": "scatter"}],
            [{"type": candlestick_plot_type}],
            [{"type": volume_bar_plot_type}],
        ]
    )

    fig.add_trace(
        go.Scatter(
            x=open_time,
            y=capital,
            name="Capital",
        ),
        row=1, col=1,
    )

    if candlestick_plot:
        open_price = candles[OPEN_PRICE_INDEX]
        fig.add_trace(
            go.Candlestick(
                x=open_time,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                name="Candles"
            ),
            row=2, col=1,
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=open_time,
                y=close_price,
                marker={"color": "#444"},
                name="Close prices",
            ),
            row=2, col=1,
        )

    low_or_close_price = low_price if candlestick_plot else close_price
    fig.add_trace(
        go.Scatter(
            x=entry_time,
            y=low_or_close_price * 0.9,
            name="Entry",
            mode="markers",
            marker={"color": "#3d8f6d", "symbol": "triangle-up"},
            customdata=__create_custom_data(entry_price, entry_side, entry_quantity),
            hovertemplate="<br>".join((
                "%{x}",
                "Price: %{customdata[0]:.2f}",
                "Side: %{customdata[1]}",
                "Quantity: %{customdata[2]:.3f}",
            )),
        ),
        row=2, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=middle_time,
            y=low_or_close_price * 0.9,
            name="Adjust",
            mode="markers",
            marker={"color": "#ff9000", "symbol": "triangle-up"},
            customdata=__create_custom_data(middle_price, middle_quantity),
            hovertemplate="<br>".join((
                "%{x}",
                "Price: %{customdata[0]:.2f}",
                "Quantity: %{customdata[1]:.3f}",
            )),
        ),
        row=2, col=1,
    )

    high_or_close_price = high_price if candlestick_plot else close_price
    fig.add_trace(
        go.Scatter(
            x=exit_time,
            y=high_or_close_price * 1.1,
            name="Exit",
            mode="markers",
            marker=dict(
                color="red",
                symbol="triangle-down",
            ),
            customdata=__create_custom_data(exit_price, exit_quantity, profit),
            hovertemplate="<br>".join((
                "%{x}",
                "Price: %{customdata[0]:.2f}",
                "Quantity: %{customdata[1]:.2f}",
                "Profit: %{customdata[2]:.2f}",
            ))
        ),
        row=2, col=1,
    )
    fig.update_xaxes(rangeslider={'visible': False}, row=2, col=1)

    if volume_bar_plot:
        fig.add_trace(
            go.Bar(
                x=open_time,
                y=volume,
                name="Volume",
                marker={"color": "#2CA02C"},
            ),
            row=3, col=1,
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=open_time,
                y=volume,
                name="Volume",
                marker={"color": "#2CA02C"},
            ),
            row=3, col=1,
        )

    fig.update_yaxes(tickformat=',.2f')

    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
    )

    return fig


def plot_backtest_results(
        candles: np.ndarray,
        positions: np.ndarray,
        add_or_reduce_positions: np.ndarray,
        start_cash: float,
        candlestick_plot=False,
        volume_bar_plot=False,
):
    entry_time = positions[TIME_INDEX]
    entry_price = positions[PRICE_INDEX]
    quantity = positions[QUANTITY_INDEX]

    middle_time = add_or_reduce_positions[TIME_INDEX]
    middle_price = add_or_reduce_positions[PRICE_INDEX]
    middle_quantity = add_or_reduce_positions[QUANTITY_INDEX]

    exit_time = positions[EXIT_TIME_INDEX]
    exit_price = positions[EXIT_PRICE_INDEX]
    exit_quantity = positions[EXIT_QUANTITY_INDEX]
    side = positions[SIDE_INDEX]
    profit = positions[PROFIT_INDEX]

    candle_open_times = candles[OPEN_TIME_INDEX]

    ext_entry_time = map_match(candle_open_times, entry_time)
    ext_exit_time = map_match(candle_open_times, exit_time)
    ext_middle_time = map_match(candle_open_times, middle_time)

    ext_entry_data = {
        key: assign_where_not_zero(ext_entry_time, val)
        for key, val in {"entry_price": entry_price, "entry_quantity": quantity, "entry_side": side}.items()
    }
    ext_middle_data = {
        key: assign_where_not_zero(ext_middle_time, val)
        for key, val in {"middle_price": middle_price, "middle_quantity": middle_quantity}.items()
    }
    ext_exit_data = {
        key: assign_where_not_zero(ext_exit_time, val)
        for key, val in {"exit_price": exit_price, "exit_quantity": exit_quantity, "profit": profit}.items()
    }

    ext_capital = np.cumsum(ext_exit_data["profit"]) + start_cash

    ext_entry_time[ext_entry_time == 0.0] = np.nan
    ext_middle_time[ext_middle_time == 0.0] = np.nan
    ext_exit_time[ext_exit_time == 0.0] = np.nan

    fig = create_plots(
        candles=candles,
        candlestick_plot=candlestick_plot,
        volume_bar_plot=volume_bar_plot,
        capital=ext_capital,
        entry_time=ext_entry_time,
        exit_time=ext_exit_time,
        middle_time=ext_middle_time,
        **ext_entry_data,
        **ext_exit_data,
        **ext_middle_data,
    )

    fig.show()


def create_dash_app(fig):
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Checklist(
            options=[
                {'label': 'Logarithmic', 'value': 'log'},
            ],
            value=['log'],
            labelStyle={'display': 'inline-block'}
        ),
        dcc.Graph(id="trade_result", figure=fig)
    ])

    app.run_server(debug=True)
