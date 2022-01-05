from backtest.helper import run_backtest
from consts.candle_index import *
from indicator.ma_trend import MATrendIndicator
from indicator.mixed.rsi_with_ma_trend import RSIWithMATrendIndicator

from indicator import RSIIndicator
from plot import Plot
from plot.plotter import CandlestickType
from strategy import IndicatorStrategy


if __name__ == "__main__":

    start_cash = 1000

    upper_limit = 70
    lower_limit = 30

    rsi_ind = RSIIndicator(upper_limit=upper_limit, lower_limit=lower_limit)
    ma_trend_ind = MATrendIndicator(
        slow_period=200, fast_period=50, fast_column_index=CLOSE_PRICE_INDEX,
        slow_type="EMA", fast_type="EMA", slow_column_index=CLOSE_PRICE_INDEX,
    )
    rsi_with_trend_ind = RSIWithMATrendIndicator(rsi=rsi_ind, ma_trend=ma_trend_ind)

    run_backtest(
        symbol="BTCUSDT",
        interval="1h",
        market="FUTURES",
        db_path="data/binance_candles.db",
        skip=256,
        trade_ratio=0.85,
        start_cash=1000,
        leverage=1,
        strategy_type=IndicatorStrategy,
        indicator=rsi_with_trend_ind,
        candlestick_type=CandlestickType.HEIKIN_ASHI,
        extra_plots=[
            Plot(
                number=3,
                type="scatter",
                data_callback=rsi_ind,
                params=[
                    dict(
                        y=RSIIndicator.RSI_INDEX,
                        name="RSI",
                    ),
                    dict(
                        constant_y=rsi_ind.upper_limit,
                        name="Upper RSI",
                        marker={"color": "blue"},
                    ),
                    dict(
                        constant_y=rsi_ind.lower_limit,
                        name="Lower RSI",
                        marker={"color": "blue"},
                    ),
                ]
            ),
            Plot(
                number=2,
                type="scatter",
                data_callback=ma_trend_ind,
                params=[
                    dict(
                        y=MATrendIndicator.SLOW_MA_INDEX,
                        name="Slow MA",
                        opacity=0.8,
                        line=dict(
                            width=2,
                            color="red",
                        )
                    ),
                    dict(
                        y=MATrendIndicator.FAST_MA_INDEX,
                        name="Fast MA",
                        opacity=0.8,
                        line=dict(
                            width=1.25,
                            color="orange",
                        )
                    )
                ]
            )
        ]
    )
