from typing import Dict, Optional, Union

import pandas as pd
from crypto_data.binance.extract import Limit
from crypto_data.shared.candle_db import CandleDB

from strategy_runner import BinanceRunner, BacktestRunner
from util import read_config


def get_candles_from_config(
    config: Dict[str, any]
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    import crypto_data.binance.extract

    def create_limit(limit_config: Dict[str, any]) -> Optional[Limit]:
        if limit_config["type"] != "ignore":
            return Limit(**limit_config["limit"])

    symbols = config["symbols"]
    interval = config["interval"]
    market = config["market"]
    candle_db = CandleDB(config["database_path"])
    columns = config["columns"]
    limit = create_limit(config["limit"])

    def get_candles(symbol: str):
        return crypto_data.binance.extract.get_candles(
            symbol=symbol,
            interval=interval,
            market=str(market).upper(),
            db=candle_db,
            columns=columns,
            limit=limit,
        )

    if len(symbols) == 0:
        raise ValueError("At least one symbol should be given!")
    elif len(symbols) == 1:
        return get_candles(symbol=symbols[0])

    return {symbol: get_candles(symbol=symbol) for symbol in symbols}


def run_binance_strategy_from_config():
    config = read_config("configs/trading_bot_config.yaml")
    binance_keys = read_config("configs/binance_secrets.json")

    candles = get_candles_from_config(config)

    runner = BinanceRunner.from_config(
        candles=candles,
        config=config,
        api_key=binance_keys["api_key"],
        api_secret=binance_keys["api_secret"],
    )
    runner.run(on_candle=lambda c: print(c))


def run_backtest_strategy_from_config():
    config = read_config("configs/trading_bot_config.yaml")

    candles = get_candles_from_config(config)

    runner = BacktestRunner.from_config(
        candles=candles,
        config=config,
    )
    runner.run()


if __name__ == "__main__":
    run_backtest_strategy_from_config()
