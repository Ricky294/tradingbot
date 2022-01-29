from backtest.strategy_runner import backtest_strategy
from shared.const.candle_index import *

from indicator.signal import RSIIndicator, DoubleMATrendIndicator
from indicator.signal.mixed import RSIWithMATrendIndicator

from indicator.sltp import ATRIndicator, RelativeToPrice

from plot import Plot
from plot.plotter import CandlestickType
from strategy import IndicatorStrategy

if __name__ == "__main__":

    start_cash = 1000

    upper_limit = 70
    lower_limit = 30

    rsi_ind = RSIIndicator(upper_limit=upper_limit, lower_limit=lower_limit)
    ma_trend_ind = DoubleMATrendIndicator(
        slow_period=200, fast_period=50, fast_column_index=CLOSE_PRICE_INDEX,
        slow_type="EMA", fast_type="EMA", slow_column_index=CLOSE_PRICE_INDEX,
    )
    rsi_with_trend_ind = RSIWithMATrendIndicator(rsi=rsi_ind, ma_trend=ma_trend_ind)
    relative_ind = RelativeToPrice(sl_multiple=0.95, tp_multiple=1.1)

    atr_ind = ATRIndicator()

    backtest_strategy(
        symbol="BTCUSDT",
        interval="1h",
        market="FUTURES",
        db_path="data/binance_candles.db",
        skip=256,
        trade_ratio=0.8,
        start_cash=1000,
        leverage=5,
        strategy_type=IndicatorStrategy,
        indicators=[rsi_with_trend_ind],
        sltp_indicator=relative_ind,
        candlestick_type=CandlestickType.LINE,
        log_scale=False,
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
                        y=DoubleMATrendIndicator.SLOW_MA_INDEX,
                        name="Slow MA",
                        opacity=0.8,
                        line=dict(
                            width=2,
                            color="red",
                        )
                    ),
                    dict(
                        y=DoubleMATrendIndicator.FAST_MA_INDEX,
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
