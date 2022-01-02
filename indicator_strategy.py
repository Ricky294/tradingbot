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
from binance_ import BinanceFuturesTrader
from binance_.helpers import get_symbol_info
from consts.candle_column_index import *
from indicator.ma_trend import MATrendIndicator
from indicator.mixed.rsi_with_ma_trend import RSIWithMATrendIndicator
from model import Balance

from indicator import RSIIndicator, MACDIndicator
from plot.plotly import plot_results, ExtraGraph

from strategy import SimpleStrategy
from strategy.macd import MACDStrategy
from util.common import read_config


def backtest_trading():
    symbol = "BTCUSDT"
    interval = "15m"
    market = "FUTURES"
    skip = 256
    trade_ratio = 0.8
    start_cash = 1000
    leverage = 1

    candle_db = CandleDB("data/binance_candles.db")
    candles = get_candles(
        symbol=symbol,
        interval=interval,
        market=market,
        db=candle_db,
        columns=[OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
    ).to_numpy()

    symbol_info = get_symbol_info(Client(), symbol)

    trader = BacktestFuturesTrader(
        interval=interval,
        trade_ratio=trade_ratio,
        symbol_info=symbol_info,
        balance=Balance(asset="USDT", total=start_cash, available=start_cash),
        leverage=leverage,
    )

    upper_limit = 70
    lower_limit = 30
    rsi_ind = RSIIndicator(upper_limit=upper_limit, lower_limit=lower_limit)
    ma_trend_ind = MATrendIndicator(slow_period=30, fast_period=10, slow_type="SMA", fast_type="SMA")

    rsi_with_trend_ind = RSIWithMATrendIndicator(rsi=rsi_ind, ma_trend=ma_trend_ind)

    backtest_indicator = BacktestIndicator(candles=candles, indicator=rsi_with_trend_ind, skip=skip)

    strategy = SimpleStrategy(
        symbol=symbol,
        trader=trader,
        indicator=backtest_indicator,
    )

    run_backtest(
        candles=candles,
        strategy=strategy,
        skip=skip,
    )

    upper_rsi_series = np.empty(candles.shape[0])
    upper_rsi_series.fill(upper_limit)

    lower_rsi_series = np.empty(candles.shape[0])
    lower_rsi_series.fill(lower_limit)

    plot_results(
        candles=candles.T,
        positions=positions_to_array(trader.positions),
        add_or_reduce_positions=add_or_reduce_positions_to_array(trader.positions),
        start_cash=start_cash,
        candlestick_plot=False,
        extra_graphs=[
            ExtraGraph(
                chart_number=2,
                graph_type="scatter",
                graph_params=[
                    dict(
                        y=backtest_indicator.indicator_data["slow_ma"],
                        name="Slow MA",
                    ),
                    dict(
                        y=backtest_indicator.indicator_data["fast_ma"],
                        name="Fast MA",
                    ),
                ],
            ),
            ExtraGraph(
                chart_number=3,
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

