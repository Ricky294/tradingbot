import importlib
from typing import List

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
    EXIT_PRICE_INDEX,
    SIDE_INDEX,
    PROFIT_INDEX,
    EXIT_QUANTITY_INDEX,
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
from statistics.basic import (
    win_loss_rate,
    biggest_looser,
    biggest_winner,
)
from util.numpy_util import map_match


class ExtraGraph:

    def __init__(self, row_index: int, graph_type: str, graph_params: dict):
        self.row_index = row_index
        self.graph_params = graph_params
        self.graph_type = graph_type


def __create_custom_data(*arrays: np.ndarray):
    return np.stack(tuple(arrays), axis=-1)


def plot_results(
        candles: np.ndarray,
        positions: np.ndarray,
        add_or_reduce_positions: np.ndarray,
        start_cash: float,
        extra_graphs: List[ExtraGraph] = None,
        candlestick_plot=False,
):
    candle_open_times = candles[OPEN_TIME_INDEX]

    entry_time = map_match(candle_open_times, positions[TIME_INDEX])
    entry_price = assign_where_not_zero(entry_time, positions[PRICE_INDEX])
    quantity = assign_where_not_zero(entry_time, positions[QUANTITY_INDEX])
    side = assign_where_not_zero(entry_time, positions[SIDE_INDEX])

    middle_time = map_match(candle_open_times, add_or_reduce_positions[TIME_INDEX])
    middle_quantity = assign_where_not_zero(middle_time, add_or_reduce_positions[QUANTITY_INDEX])
    middle_price = assign_where_not_zero(middle_time, add_or_reduce_positions[PRICE_INDEX])

    exit_time = map_match(candle_open_times, positions[EXIT_TIME_INDEX])
    exit_price = assign_where_not_zero(exit_time, positions[EXIT_PRICE_INDEX])
    exit_quantity = assign_where_not_zero(exit_time, positions[EXIT_QUANTITY_INDEX])
    profit = assign_where_not_zero(exit_time, positions[PROFIT_INDEX])

    capital = np.cumsum(profit) + start_cash

    entry_time[entry_time == 0.0] = np.nan
    middle_time[middle_time == 0.0] = np.nan
    exit_time[exit_time == 0.0] = np.nan

    def create_plots():
        nonlocal entry_time
        nonlocal middle_time
        nonlocal exit_time

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

        max_row = 2

        extra_graph_max_row = 0

        if extra_graphs is not None:
            extra_graph_max_row = max((graph.row_index for graph in extra_graphs))

        if extra_graph_max_row > 2:
            max_row = extra_graph_max_row

        row_heights = [1 for _ in range(max_row)]
        row_heights[1] = 2

        specs = [
            [{"type": "scatter"}],
            [{"secondary_y": True}],
        ]

        if extra_graphs is not None:
            specs.extend([[{"type": graph.graph_type.lower()}] for graph in extra_graphs])

        fig = make_subplots(
            rows=max_row, cols=1,
            column_widths=[1.0],
            row_heights=row_heights,
            shared_xaxes=True,
            horizontal_spacing=0.0,
            vertical_spacing=0.02,
            specs=specs,
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
                secondary_y=False,
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
                secondary_y=False,
            )

        low_or_close_price = low_price if candlestick_plot else close_price
        fig.add_trace(
            go.Scatter(
                x=entry_time,
                y=low_or_close_price * 0.9,
                name="Entry",
                mode="markers",
                marker={"color": "#3d8f6d", "symbol": "triangle-up"},
                customdata=__create_custom_data(entry_price, side, quantity),
                hovertemplate="<br>".join((
                    "%{x}",
                    "Price: %{customdata[0]:.2f}",
                    "Side: %{customdata[1]}",
                    "Quantity: %{customdata[2]:.3f}",
                )),
            ),
            secondary_y=False,
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
            secondary_y=False,
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
            secondary_y=False,
            row=2, col=1,
        )
        fig.update_xaxes(rangeslider={'visible': False}, row=2, col=1)

        fig.add_trace(
            go.Scatter(
                x=open_time,
                y=volume,
                name="Volume",
                marker={"color": "#2CA02C"},
                opacity=0.2,
                hoverinfo='skip',
            ),
            secondary_y=True,
            row=2, col=1,
        )

        if extra_graphs is not None:
            for graph in extra_graphs:
                graph_module = importlib.import_module(f'plotly.graph_objects')
                graph_class = getattr(graph_module, graph.graph_type.capitalize())
                fig.add_trace(
                    graph_class(
                        x=open_time,
                        **graph.graph_params
                    ),
                    row=graph.row_index, col=1,
                )

        fig.update_layout(
            margin=dict(l=10, r=10, t=20, b=10),
        )
        fig.update_yaxes(tickformat=',.2f', visible=False, showticklabels=False, secondary_y=True)
        fig.layout.yaxis2.showgrid = False

        return fig

    def include_info_on_figure():
        wins, losses, win_rate = win_loss_rate(profit)
        biggest_loss = biggest_looser(profit)
        biggest_win = biggest_winner(profit)

        fig.add_annotation(
            text="<br>".join([
                f"Wins: {wins}, Losses: {losses}, Win rate: {win_rate:.2f}",
                f"Largest win: {biggest_win:.2f}, Largest loss: {biggest_loss:.2f}",
            ]),
            align="left",
            xref="x domain", yref="y domain",
            font=dict(
                size=8,
            ),
            x=0.005, y=0.99, showarrow=False,
            row=2, col=1,
        )

        percentage_profit = ((capital[-1] - start_cash) / start_cash) * 100

        fig.add_annotation(
            text="<br>".join([
                f"Final balance: {capital[-1]:.2f} ({'+' if percentage_profit > 0 else ''}{percentage_profit:.3f}%)",
            ]),
            align="left",
            xref="x domain", yref="y domain",
            font=dict(
                size=8,
            ),
            x=0.005, y=0.99, showarrow=False,
            row=1, col=1,
        )

    fig = create_plots()
    include_info_on_figure()
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
