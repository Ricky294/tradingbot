import numpy as np
import pandas as pd
from binance.client import Client
from crypto_data.binance.pd.extract import get_candles
from crypto_data.shared.candle_db import CandleDB

from backtest import (
    BacktestFuturesTrader,
    BacktestIndicator,
    run_backtest,
    positions_to_array,
)
from backtest.transform_positions import add_or_reduce_positions_to_array, SIDE_INDEX
from consts.candle_column_index import *
from model import Balance

from indicator import RSIIndicator, MACDIndicator
from plot.plotly import plot_results, ExtraGraph

from strategy import RSIStrategy
from strategy.macd import MACDStrategy
from util.common import read_config
import plotly.graph_objects as go


def backtest_trading():
    symbol = "BTCUSDT"
    interval = "12h"
    market = "FUTURES"
    skip = 256
    trade_ratio = 0.1
    start_cash = 1000

    candle_db = CandleDB("data/binance_candles.db")
    candles = get_candles(
        symbol=symbol,
        interval=interval,
        market=market,
        db=candle_db,
        columns=[OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
    ).to_numpy()

    binance_keys = read_config("secrets/binance_secrets.json")
    client = Client(api_key=binance_keys["api_key"], api_secret=binance_keys["api_secret"])

    trader = BacktestFuturesTrader(
        client=client,
        interval=interval,
        trade_ratio=trade_ratio,
        balance=Balance(asset="USDT", total=start_cash, available=start_cash),
    )
    indicator = RSIIndicator()
    backtest_indicator = BacktestIndicator(candles=candles, indicator=indicator, skip=skip)

    strategy = RSIStrategy(
        symbol=symbol,
        trader=trader,
        indicator=backtest_indicator,
    )

    run_backtest(
        candles=candles,
        strategy=strategy,
    )

    upper_rsi_series = np.empty(candles.shape[0])
    upper_rsi_series.fill(70)

    lower_rsi_series = np.empty(candles.shape[0])
    lower_rsi_series.fill(30)

    plot_results(
        candles=candles.T,
        positions=positions_to_array(trader.positions),
        add_or_reduce_positions=add_or_reduce_positions_to_array(trader.positions),
        start_cash=start_cash,
        candlestick_plot=False,
        extra_graphs=[
            ExtraGraph(
                row_index=3,
                graph_type="scatter",
                graph_params=[
                    dict(
                        y=backtest_indicator.indicator_data["rsi"],
                        name="RSI",
                    ),
                    dict(
                        y=upper_rsi_series,
                        name="Upper RSI",
                        marker={"color": "blue"},
                    ),
                    dict(
                        y=lower_rsi_series,
                        name="Lower RSI",
                        marker={"color": "blue"},
                    ),
                ]
            ),
        ],
    )


if __name__ == "__main__":
    backtest_trading()

