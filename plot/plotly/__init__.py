import numpy as np
import pandas as pd

import dash
from dash import dcc
from dash import html

import plotly.graph_objects as go
from plotly.subplots import make_subplots


from backtest import BacktestFuturesTrader
from consts.candle_column_index import (
    OPEN_TIME_INDEX,
    OPEN_PRICE_INDEX,
    HIGH_PRICE_INDEX,
    LOW_PRICE_INDEX,
    CLOSE_PRICE_INDEX,
    VOLUME_INDEX,
)
from plot.transform import extend_data


def __create_custom_data(*arrays: np.ndarray):
    return np.stack(tuple(arrays), axis=-1)


def create_plots(
        open_time, open_price, close_price, volume,
        profit, capital, entry_time, entry_price, exit_time, exit_price, side, quantity,
        high_price=None, low_price=None,
        candlestick_plot=True, volume_bar_plot=True
):
    if candlestick_plot and (high_price is None or low_price is None):
        raise ValueError("high_price and low_price parameter is required if candlestick_plot is True")

    open_time = pd.to_datetime(open_time, unit="s")
    entry_time = pd.to_datetime(entry_time, unit="s")
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
                name="Close prices"
            ),
            row=2, col=1,
        )

    low_or_close_price = low_price if candlestick_plot else close_price
    fig.add_trace(
        go.Scatter(
            x=entry_time,
            y=low_or_close_price * 0.9,
            name="Entries",
            mode="markers",
            marker={"color": "green", "symbol": "triangle-up"},
            customdata=__create_custom_data(entry_price, side, quantity),
            hovertemplate="<br>".join((
                "%{x}",
                "Entry: %{customdata[0]:.2f}",
                "Side: %{customdata[1]}",
                "Quantity: %{customdata[2]:.3f}",
            )),
        ),
        row=2, col=1,
    )

    high_or_close_price = high_price if candlestick_plot else close_price
    fig.add_trace(
        go.Scatter(
            x=exit_time,
            y=high_or_close_price * 1.1,
            name="Exits",
            mode="markers",
            marker={"color": "red", "symbol": "triangle-down"},
            customdata=__create_custom_data(exit_price, profit),
            hovertemplate="<br>".join((
                "%{x}",
                "Exit: %{customdata[0]:.2f}",
                "Profit: %{customdata[1]:.2f}"
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

    return fig


def plot_backtest_results(
        candles: np.ndarray,
        trader: BacktestFuturesTrader,
        candlestick_plot=False,
        volume_bar_plot=False,
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

    fig = create_plots(
        open_time=candles_T[OPEN_TIME_INDEX],
        open_price=candles_T[OPEN_PRICE_INDEX],
        high_price=candles_T[HIGH_PRICE_INDEX],
        low_price=candles_T[LOW_PRICE_INDEX],
        close_price=candles_T[CLOSE_PRICE_INDEX],
        volume=candles_T[VOLUME_INDEX],
        candlestick_plot=candlestick_plot,
        volume_bar_plot=volume_bar_plot,
        **extended_data,
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
