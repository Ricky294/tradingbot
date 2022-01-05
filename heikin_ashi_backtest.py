from backtest.helper import run_backtest
from consts.candle_index import *
from indicator.heikin_ashi import HeikinAshiIndicator
from indicator.ma_trend import MATrendIndicator

from indicator.mixed.heikin_ashi_ma_trend import HeikinAshiMATrendIndicator
from plot import Plot
from plot.plotter import CandlestickType
from strategy import IndicatorStrategy


if __name__ == "__main__":

    start_cash = 1000

    upper_limit = 70
    lower_limit = 30

    ha_ind = HeikinAshiIndicator()
    ma_trend_ind = MATrendIndicator(
        slow_period=30, fast_period=10, fast_column_index=CLOSE_PRICE_INDEX,
        slow_type="EMA", fast_type="EMA", slow_column_index=CLOSE_PRICE_INDEX,
    )

    ha_ma_trend_ind = HeikinAshiMATrendIndicator(ha=ha_ind, ma_trend=ma_trend_ind)

    run_backtest(
        symbol="BTCUSDT",
        interval="15m",
        market="FUTURES",
        db_path="data/binance_candles.db",
        skip=256,
        trade_ratio=0.85,
        start_cash=1000,
        leverage=1,
        strategy_type=IndicatorStrategy,
        indicator=ha_ma_trend_ind,
        candlestick_type=CandlestickType.LINE,
        extra_plots=[
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
