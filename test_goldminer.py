from pathlib import Path

from binance.client import Client
from crypto_data.binance.pd.extract import get_candles
from crypto_data.binance.schema import *
from crypto_data.shared.candle_db import CandleDB

from backtest import BacktestFuturesTrader, run_backtest
from model import Balance

from plot.plotly import plot_results
from strategy.goldminer import GoldMinerStrategy


def backtest_trading():
    symbol = "BTCUSDT"
    interval = "5m"
    market = "FUTURES"

    db_path = Path(".cache", "candles")
    if not db_path.exists():
        db_path.mkdir()
    skip = 512
    trade_ratio = 0.2
    starting_cash = 1000

    candle_db = CandleDB(str(db_path.joinpath("binance_candles.db")))
    candles = get_candles(
        symbol=symbol,
        interval=interval,
        market=market,
        db=candle_db,
        columns=[OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
    )
    candles = candles.to_numpy()
    candles = candles[int(0.7 * len(candles)):]

    client = Client()
    trader = BacktestFuturesTrader(
        client=client,
        interval=interval,
        trade_ratio=trade_ratio,
        balance=Balance(asset="USDT", balance=starting_cash, free=starting_cash)
    )

    strategy = GoldMinerStrategy(symbol=symbol, trader=trader)
    run_backtest(
        candles=candles,
        strategy=strategy,
        trader=trader,
        skip=skip,
    )

    plot_results(
        candles=candles,
        trader=trader,
    )


if __name__ == "__main__":
    backtest_trading()
