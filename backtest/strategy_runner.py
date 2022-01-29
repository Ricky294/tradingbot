from typing import Type, Union, List, Callable, Iterable

from plotly.subplots import make_subplots

from crypto_data.binance.pd.extract import get_candles
from crypto_data.shared.candle_db import CandleDB

from trader.backtest import run_backtest
from trader.backtest.futures_trader import BacktestFuturesTrader
from trader.backtest.tape import ArrayTape
from trader.backtest.plot import Plot
from trader.backtest.plotter import plot_backtest_results

from trader.core.model import Balance
from trader.core.enum import CandlestickType
from trader.core.const.candle_index import *
from trader.core.strategy import Strategy

from indicator.signal import Indicator, OptimizedIndicator
from indicator.sltp import SLTPIndicator

from strategy import IndicatorStrategy

from statistics import TradeReport


def backtest_strategy(
        symbol: str,
        interval: str,
        market: str,
        db_path: any,
        trade_ratio: float,
        start_cash: float,
        leverage: int,
        maker_fee_rate: float,
        taker_fee_rate: float,
        strategy_type: Type[IndicatorStrategy],
        indicators: List[Indicator],
        skip=0,
        exit_indicators: List[Indicator] = None,
        sltp_indicator: SLTPIndicator = None,
        log_scale=False,
        candlestick_type=CandlestickType.LINE,
        extra_plots: List[Plot] = None,
        create_report=True,
):
    trader = BacktestFuturesTrader(
        interval=interval,
        symbol=symbol,
        maker_fee_rate=maker_fee_rate,
        taker_fee_rate=taker_fee_rate,
        balance=Balance(asset="USDT", total=start_cash, available=start_cash),
        leverage=leverage,
    )

    columns = [OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME]

    candle_db = CandleDB(db_path)

    candles = get_candles(
        symbol=symbol,
        interval=interval,
        market=market,
        db=candle_db,
        columns=columns,
    ).to_numpy()[skip:]

    indicator_tapes = [
        OptimizedIndicator(ArrayTape.from_callback(array=candles, callback=ind))
        for ind in indicators
    ]

    exit_indicator_tapes = [
        OptimizedIndicator(ArrayTape.from_callback(array=candles, callback=ind))
        for ind in exit_indicators
    ]

    strategy = strategy_type(
        symbol=symbol,
        trader=trader,
        trade_ratio=trade_ratio,
        indicators=indicator_tapes,
        leverage=leverage,
        sltp_indicator=sltp_indicator,
        exit_indicators=exit_indicator_tapes,
    )

    run_backtest(
        candles,
        strategy,
    )

    report = TradeReport(
        start_cash=start_cash,
        trade_ratio=trade_ratio,
        leverage=leverage,
        positions=trader.positions,
        interval=interval,
        candles=candles,
        indicators=indicators,
    )

    plot_backtest_results(
        candles=candles.T,
        trader=trader,
        start_cash=start_cash,
        log_scale=log_scale,
        candlestick_type=candlestick_type,
        extra_plots=extra_plots,
    )

    if create_report:
        fig = make_subplots(
            rows=3, cols=1,
            horizontal_spacing=0.0,
            vertical_spacing=0.02,
            specs=[
                [{"type": "table"}],
                [{"type": "table"}],
                [{"type": "table"}]
            ],
            subplot_titles=("Basic info", "Trade results", "Indicators")
        )

        fig.add_trace(
            report.create_basic_info_table(),
            row=1, col=1,
        )

        fig.add_trace(
            report.create_trade_result_table(),
            row=2, col=1,
        )

        fig.add_trace(
            report.create_indicator_table(),
            row=3, col=1,
        )

        fig.show()


class TradeVariable:

    def __init__(
            self,
            interval: str,
            trade_ratio: float,
            leverage: int,
            indicators: Iterable[Indicator],
            sltp_indicator: SLTPIndicator = None,
            exit_indicator: Indicator = None,
    ):
        self.interval = interval
        self.trade_ratio = trade_ratio
        self.leverage = leverage
        self.indicators = indicators

        if sltp_indicator is None and exit_indicator is None:
            raise ValueError("At least sltp or exit indicator must not be None!")
        self.sltp_indicator = sltp_indicator
        self.exit_indicator = exit_indicator


def __run_backtest_wrapper(args):
    extra_plots = None

    if args[12] is not None:
        extra_plots = args[12](*args[9])

    return backtest_strategy(
        symbol=args[0],
        interval=args[1],
        market=args[2],
        db_path=args[3],
        skip=args[4],
        trade_ratio=args[5],
        start_cash=args[6],
        leverage=args[7],
        strategy_type=args[8],
        indicators=args[9],
        sltp_indicator=args[10],
        exit_indicators=args[11],
        extra_plots=extra_plots,
    )


def backtest_multiple_strategy(
        symbol: str,
        market: str,
        db_path: any,
        skip: int,
        start_cash: float,
        strategy_type: Type[Union[Strategy, IndicatorStrategy]],
        variables: List[TradeVariable],
        extra_plots_callback: Callable[[any], List[Plot]] = None,
):
    def create_arg_list(params: TradeVariable):
        return (
            symbol, params.interval, market, db_path, skip, params.trade_ratio, start_cash,
            params.leverage, strategy_type, params.indicators, params.sltp_indicator,
            params.exit_indicator, extra_plots_callback,
        )

    __run_backtest_wrapper([create_arg_list(variable) for variable in variables][0])

    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     executor.map(
    #         __run_backtest_wrapper, [create_arg_list(variable) for variable in variables]
    #     )
