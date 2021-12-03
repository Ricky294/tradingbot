from typing import Dict, Union

from binance.client import Client

from crypto_data.binance.candle import StreamCandle
from crypto_data.binance.extract import get_candles, Limit
from crypto_data.binance.schema import (
    OPEN_TIME,
    OPEN_PRICE,
    CLOSE_PRICE,
    HIGH_PRICE,
    LOW_PRICE,
    VOLUME,
)
from crypto_data.binance.stream import candle_stream, candle_multi_stream
from crypto_data.shared.candle_db import CandleDB

from backtest import backtest_candle_stream, BacktestClient, BacktestFuturesTrader
from binance_ import BinanceFuturesTrader
from indicator import Indicator
from strategy import SingleSymbolStrategy, MultiSymbolStrategy
from abstract import FuturesTrader
from util import read_config, get_object_from_module


def run_futures_strategy(
    interval: str,
    strategy: Union[SingleSymbolStrategy, MultiSymbolStrategy],
    candle_db: CandleDB,
    limit: Limit = None,
):
    def __get_candles(symbol: str):
        return get_candles(
            symbol=symbol,
            interval=interval,
            market="FUTURES",
            db=candle_db,
            columns=[
                OPEN_TIME,
                OPEN_PRICE,
                CLOSE_PRICE,
                HIGH_PRICE,
                LOW_PRICE,
                VOLUME,
            ],
            limit=limit,
        )

    def on_candle(candle: StreamCandle):
        print(candle)

    if isinstance(strategy, MultiSymbolStrategy):
        candles = {symbol: __get_candles(symbol) for symbol in strategy.symbols}
        candle_multi_stream(
            interval=interval,
            market="FUTURES",
            symbol_candles=candles,
            on_candle=on_candle,
            on_candle_close=strategy,
        )
    else:
        candles = __get_candles(strategy.symbol)
        candle_stream(
            symbol=strategy.symbol,
            interval=interval,
            market="FUTURES",
            candles=candles,
            on_candle=on_candle,
            on_candle_close=strategy,
        )
        backtest_candle_stream(candles=candles, on_candle_close=strategy)


class ConfigError(Exception):
    pass


def create_indicators(indicators_config: Dict[str, Dict]) -> Dict[str, Indicator]:
    indicators = {
        name: get_object_from_module(
            module_name="indicator", object_name=indicator.pop("type")
        )(**indicator)
        for name, indicator in indicators_config.items()
    }
    return indicators


def create_strategy(
    config: Dict[str, any], trader: FuturesTrader
) -> Union[SingleSymbolStrategy, MultiSymbolStrategy]:
    indicators_config = config.pop("indicators")
    indicators: Dict[str, Indicator] = create_indicators(indicators_config)

    strategy_class = get_object_from_module(
        module_name="strategy", object_name=config.pop("type")
    )

    return strategy_class(**config, trader=trader, **indicators)


def create_strategy_objects_from_config(
    client: Union[Client, BacktestClient], config: Dict[str, any]
):

    try:
        limit = None
        if config["limit"]["type"] != "ignore":
            limit = Limit(**config["limit"])

        trader_config = config.pop("trader")
        if isinstance(client, Client):
            trader = BinanceFuturesTrader(client=client, **trader_config)
        elif isinstance(client, BacktestClient):
            trader = BacktestFuturesTrader(client=client, **trader_config)
        else:
            raise ValueError("'trader' must be type of Client or BacktestClient")

        strategy = create_strategy(config=config["strategy"], trader=trader)

        candle_db = CandleDB(config["database_path"])

        return {
            "interval": config["interval"],
            "candle_db": candle_db,
            "strategy": strategy,
            "limit": limit,
        }
    except KeyError as e:
        raise ConfigError(f"'{e.args[0]}' is missing from config.")


def run_strategy_from_config(secrets_path: str, config_path: str):
    config = read_config(config_path)

    mode = config.pop("mode").lower()
    if mode == "live":
        client = Client(**read_config(secrets_path))
    elif mode == "backtest":
        client = BacktestClient()
    else:
        raise ConfigError("'mode' must be either 'live' or 'backtest'")

    strategy_objects = create_strategy_objects_from_config(client, config)

    run_futures_strategy(**strategy_objects)


if __name__ == "__main__":
    run_strategy_from_config(
        secrets_path="secrets/binance_secrets.json",
        config_path="configs/trading_bot_config.yaml",
    )
