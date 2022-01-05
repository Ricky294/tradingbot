from typing import Optional, Type, Union, List, Callable

from binance.client import Client
from crypto_data.binance.pd.extract import get_candles
from crypto_data.shared.candle_db import CandleDB

import backtest

from backtest.futures_trader import BacktestFuturesTrader
from backtest.indicator import BacktestIndicator

from backtest.transform_positions import add_or_reduce_positions_to_array, positions_to_array
from binance_.helpers import get_symbol_info
from consts.candle_index import *
from model import Balance

from indicator import Indicator
from plot import Plot
from plot.plotter import plot_results, CandlestickType

from strategy import IndicatorStrategy, Strategy

import concurrent.futures


def run_backtest(
        symbol: str,
        interval: str,
        market: str,
        db_path: any,
        skip: int,
        trade_ratio: float,
        start_cash: float,
        leverage: float,
        strategy_type: Type[Union[Strategy, IndicatorStrategy]],
        indicator: Optional[Indicator] = None,
        candlestick_type=CandlestickType.LINE,
        extra_plots: Optional[List[Plot]] = None,
):

    candle_db = CandleDB(db_path)
    candles = get_candles(
        symbol=symbol,
        interval=interval,
        market=market,
        db=candle_db,
        columns=[OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
    ).to_numpy()

    candles = candles[skip:]

    symbol_info = get_symbol_info(Client(), symbol)

    trader = BacktestFuturesTrader(
        interval=interval,
        trade_ratio=trade_ratio,
        symbol_info=symbol_info,
        balance=Balance(asset="USDT", total=start_cash, available=start_cash),
        leverage=leverage,
    )

    if indicator is not None:
        backtest_indicator = BacktestIndicator(candles=candles, indicator=indicator)

        strategy = strategy_type(
            symbol=symbol,
            trader=trader,
            indicator=backtest_indicator,
        )
    else:
        strategy = strategy_type(
            symbol=symbol,
            trader=trader,
        )

    backtest.run_backtest(
        candles,
        strategy,
    )

    plot_results(
        candles=candles.T,
        positions=positions_to_array(trader.positions),
        add_or_reduce_positions=add_or_reduce_positions_to_array(trader.positions),
        start_cash=start_cash,
        candlestick_type=candlestick_type,
        extra_plots=extra_plots,
    )


class TradeVariable:

    def __init__(self, interval, trade_ratio, leverage, indicator):
        self.interval = interval
        self.trade_ratio = trade_ratio
        self.leverage = leverage
        self.indicator = indicator


def __run_backtest_wrapper(args):
    extra_plots = None

    if args[10] is not None:
        extra_plots = args[10](args[9])

    return run_backtest(
        symbol=args[0],
        interval=args[1],
        market=args[2],
        db_path=args[3],
        skip=args[4],
        trade_ratio=args[5],
        start_cash=args[6],
        leverage=args[7],
        strategy_type=args[8],
        indicator=args[9],
        extra_plots=extra_plots,
    )


def run_multiple_backtest(
        symbol: str,
        market: str,
        db_path: any,
        skip: int,
        start_cash: float,
        strategy_type: Type[Union[Strategy, IndicatorStrategy]],
        variables: List[TradeVariable],
        extra_plots_callback: Optional[Callable[[any], List[Plot]]] = None,
):
    def create_arg_list(params: TradeVariable):
        return (
            symbol, params.interval, market, db_path, skip, params.trade_ratio, start_cash,
            params.leverage, strategy_type, params.indicator, extra_plots_callback
        )

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(
            __run_backtest_wrapper, [create_arg_list(variable) for variable in variables]
        )
