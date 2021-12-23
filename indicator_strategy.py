import numpy as np
from binance.client import Client
from crypto_data.binance.pd.extract import get_candles
from crypto_data.shared.candle_db import CandleDB

from backtest import BacktestFuturesTrader, BacktestIndicator, run_backtest
from backtest.futures_trader import EXIT_PROFIT_INDEX, ENTRY_SIDE_INDEX, create_position_array
from consts.candle_column_index import *
from model import Balance

from indicator import RSIIndicator
from plot.plotly import plot_backtest_results
from statistics.summary import Summary
from strategy import RSIStrategy
from util.common import read_config


def backtest_trading():
    symbol = "BTCUSDT"
    interval = "1h"
    market = "FUTURES"
    skip = 256
    trade_ratio = 0.5
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
        balance=Balance(asset="USDT", balance=start_cash, free=start_cash),
    )
    rsi_indicator = RSIIndicator()
    backtest_indicator = BacktestIndicator(candles=candles, indicator=rsi_indicator, skip=skip)

    strategy = RSIStrategy(
        symbol=symbol,
        trader=trader,
        rsi_indicator=backtest_indicator,
    )

    run_backtest(
        candles=candles,
        strategy=strategy,
    )

    candles_T = candles.T
    positions = create_position_array(trader.positions)
    capital = np.cumsum(positions[EXIT_PROFIT_INDEX]) + start_cash

    plot_backtest_results(
        candles=candles_T,
        positions=positions,
        start_cash=start_cash,
    )

    summary = Summary()
    summary.print_price_summary(
        open_time=candles_T[OPEN_TIME_INDEX],
        open_price=candles_T[OPEN_PRICE_INDEX],
        high_price=candles_T[HIGH_PRICE_INDEX],
        low_price=candles_T[LOW_PRICE_INDEX],
    )
    summary.print_trade_summary(
        start_cash=start_cash,
        capital=capital,
        side=positions[ENTRY_SIDE_INDEX],
        profit=positions[EXIT_PROFIT_INDEX],
    )


if __name__ == "__main__":
    backtest_trading()
