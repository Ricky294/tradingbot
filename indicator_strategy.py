from binance.client import Client
from crypto_data.binance.pd.extract import get_candles
from crypto_data.binance.schema import *
from crypto_data.shared.candle_db import CandleDB

from backtest import BacktestFuturesTrader, BacktestIndicator, run_backtest
from model import Balance

from indicator import RSIIndicator
from plot.plotly import plot_backtest_results
from strategy import RSIStrategy
from util.common import read_config


def backtest_trading():
    symbol = "BTCUSDT"
    interval = "12h"
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

    binance_keys = read_config("secrets/binance_secrets.json")
    client = Client(api_key=binance_keys["api_key"], api_secret=binance_keys["api_secret"])

    trader = BacktestFuturesTrader(
        client=client,
        interval=interval,
        trade_ratio=trade_ratio,
        balance=Balance(asset="USDT", balance=starting_cash, free=starting_cash)
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
        trader=trader,
        skip=skip,
    )

    plot_backtest_results(
        candles=candles,
        trader=trader,
    )


if __name__ == "__main__":
    backtest_trading()
