import numpy as np
from binance.client import Client
from crypto_data.binance.extract import get_candles
from crypto_data.binance.schema import *
from crypto_data.shared.candle_db import CandleDB

from backtest import BacktestFuturesTrader, BacktestIndicator
from backtest.futures_trader import extend_data
from consts.candle_column_index import (
    OPEN_TIME_INDEX,
    CLOSE_PRICE_INDEX,
    VOLUME_INDEX,
    HIGH_PRICE_INDEX,
    LOW_PRICE_INDEX,
    OPEN_PRICE_INDEX
)
from plot.plotly import create_plots
from indicator import RSIIndicator
from strategy import RSIStrategy
from util.generic import read_config


def run_backtest():
    symbol = "BTCUSDT"
    interval = "15m"
    market = "FUTURES"
    skip = 256
    trade_ratio = 0.5
    starting_cash = 1000

    candle_db = CandleDB("data/binance_candles.db")
    candles = get_candles(
        symbol=symbol,
        interval=interval,
        market=market,
        db=candle_db,
        columns=[OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
    )
    candles = candles.to_numpy()

    binance_keys = read_config("configs/binance_secrets.json")
    client = Client(api_key=binance_keys["api_key"], api_secret=binance_keys["api_secret"])

    trader = BacktestFuturesTrader(client=client, interval=interval, trade_ratio=trade_ratio)
    rsi_indicator = RSIIndicator()
    backtest_indicator = BacktestIndicator(candles=candles, indicator=rsi_indicator, skip=skip)

    # strategy = AIStrategy(
    #     symbol=symbol,
    #     trader=trader,
    # )

    strategy = RSIStrategy(
        symbol=symbol,
        trader=trader,
        rsi_indicator=backtest_indicator,
    )
    # candles = candles[int(0.7 * len(candles)):]
    strategy.run_backtest(candles=candles, skip=skip)

    if isinstance(strategy.trader, BacktestFuturesTrader):
        positions = strategy.trader.positions

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
            starting_capital=starting_cash,
        )

        fig = create_plots(
            open_time=candles_T[OPEN_TIME_INDEX],
            open_price=candles_T[OPEN_PRICE_INDEX],
            high_price=candles_T[HIGH_PRICE_INDEX],
            low_price=candles_T[LOW_PRICE_INDEX],
            close_price=candles_T[CLOSE_PRICE_INDEX],
            volume=candles_T[VOLUME_INDEX],
            candlestick_plot=False,
            volume_bar_plot=False,
            **extended_data,
        )

        fig.show()


if __name__ == "__main__":
    run_backtest()
