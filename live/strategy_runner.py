from typing import List, Type, Callable

from binance.client import Client
from crypto_data.binance.np.stream import candle_stream
from crypto_data.binance.pd.extract import get_candles
from crypto_data.binance.schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME
from crypto_data.shared.candle_db import CandleDB

from trader.live.binance.futures_trader import BinanceFuturesTrader
from trader.live.log import logger

from indicator.signal import Indicator
from indicator.sltp import SLTPIndicator
from strategy import IndicatorStrategy


def run_binance_strategy(
        api_key: str,
        api_secret: str,
        symbol: str,
        interval: str,
        market: str,
        db_path: any,
        trade_ratio: float,
        leverage: int,
        strategy_type: Type[IndicatorStrategy],
        indicators: List[Indicator],
        skip: int = 0,
        notify_on_trade: Callable = None,
        notify_on_next: Callable = None,
        sltp_indicator: SLTPIndicator = None,
        exit_indicators: List[Indicator] = None,
):
    client = Client(api_key=api_key, api_secret=api_secret)
    logger.info("Created binance client")

    trader = BinanceFuturesTrader(client=client)

    columns = [OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME]

    candle_db = CandleDB(db_path)

    candles = get_candles(
        symbol=symbol,
        interval=interval,
        market=market,
        db=candle_db,
        columns=columns,
    ).to_numpy()[skip:]

    strategy = strategy_type(
        symbol=symbol,
        trader=trader,
        trade_ratio=trade_ratio,
        indicators=indicators,
        leverage=leverage,
        sltp_indicator=sltp_indicator,
        exit_indicators=exit_indicators,
    )

    candle_stream(
        symbol=symbol,
        interval=interval,
        market=market,
        columns=columns,
        candles=candles,
        on_candle=lambda stream_candle: None,
        on_candle_close=strategy,
    )
