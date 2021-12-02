from binance.client import Client
from crypto_data.shared.candle_db import CandleDB

from indicator import RSIIndicator
from main import create_strategy_objects_from_config
from strategy import RSIStrategy
from trader import Trader


def test_config():
    client = Client()

    single_indicator_config = {
        "broker": "binance",
        "interval": "1h",
        "trader": {"market": "futures", "ratio": 0.9},
        "strategy": {
            "type": "RSIStrategy",
            "symbol": "btcusdt",
            "indicators": {
                "rsi": {
                    "type": "RSIIndicator",
                    "column": "close_price",
                    "time_period": 14,
                    "upper_limit": 70.0,
                    "lower_limit": 30.0,
                },
            },
        },
        "limit": {"type": "max_records", "value": 5000},
        "columns": [
            "open_time",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
            "number_of_trades",
        ],
        "database_path": "binance_candles.db",
    }

    strategy_objects = create_strategy_objects_from_config(
        client=client, config=single_indicator_config
    )

    assert isinstance(strategy_objects["strategy"], RSIStrategy)
    assert isinstance(strategy_objects["strategy"].rsi, RSIIndicator)
    assert isinstance(strategy_objects["trader"], Trader)
    assert isinstance(strategy_objects["candle_db"], CandleDB)
