from typing import List

import pandas as pd
from binance.client import Client

from crypto_data.binance.extract import get_candles
from crypto_data.binance.schema import (
    OPEN_TIME,
    OPEN_PRICE,
    CLOSE_PRICE,
    HIGH_PRICE,
    LOW_PRICE,
    VOLUME,
)
from crypto_data.binance.stream import candle_stream
from crypto_data.shared.candle_db import CandleDB

from binance_.futures import inject_trade_info
from indicator.rsi import RSI
from model.balance import Balance
from model.order import Order
from model.position import Position
from model.symbol_info import SymbolInfo
from trader.trader import Trader
from util import read_config


def candle_callback(client: Client, trade_percentage: float, candles: pd.DataFrame):
    def trade_info_callback(
        positions: List[Position],
        orders: List[Order],
        balances: List[Balance],
        info: List[SymbolInfo],
    ):
        nonlocal client
        nonlocal candles

        rsi_ind = RSI(df=candles)
        trader = Trader(client=client, indicator=rsi_ind, percentage=trade_percentage)

        print(rsi_ind)

        trader.create_orders_on_buy_signal()
        trader.create_orders_on_sell_signal()

    return trade_info_callback


def main():
    data_config = read_config("configs/data_config.yaml")
    api_keys = read_config("secrets/binance_secrets.json")

    client = Client(**api_keys)

    symbol = "btcusdt"
    interval = "5m"
    market = "futures"
    db = CandleDB("data/binance_candles.db")
    trade_percentage = 0.95

    def on_candle(candle: dict):
        print(candle)

    def on_candle_close(candles: pd.DataFrame):
        trade_info_callback = candle_callback(client, trade_percentage, candles)
        inject_trade_info(client=client, symbol=symbol, callback=trade_info_callback)

    candles_df = get_candles(
        symbol=symbol,
        interval=interval,
        market=market,
        db=db,
        columns=[
            OPEN_TIME,
            OPEN_PRICE,
            CLOSE_PRICE,
            HIGH_PRICE,
            LOW_PRICE,
            VOLUME,
        ],
    )

    candle_stream(
        symbol=symbol,
        interval=interval,
        market=market,
        candles=candles_df,
        on_candle=on_candle,
        on_candle_close=on_candle_close,
    )


if __name__ == "__main__":
    main()
