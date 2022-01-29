from trader.core.enum import CandlestickType
from trader.core.const.candle_index import *
from trader.backtest.plot import Plot

from backtest.strategy_runner import backtest_strategy

from indicator.signal import HeikinAshiIndicator, DoubleMATrendIndicator, MAPriceIndicator
from indicator.sltp import ATRIndicator

from strategy import IndicatorStrategy


if __name__ == "__main__":

    start_cash = 1000

    upper_limit = 70
    lower_limit = 30

    ha_ind = HeikinAshiIndicator()
    ha_exit_ind = HeikinAshiIndicator()
    ma_price_ex_ind = MAPriceIndicator(ma_period=200, ma_type="EMA", ma_column_index=CLOSE_PRICE_INDEX)

    ma_price_ind = MAPriceIndicator(ma_period=200, ma_type="EMA", ma_column_index=CLOSE_PRICE_INDEX)
    ma_trend_ind = DoubleMATrendIndicator(
        slow_period=200, fast_period=50, fast_column_index=CLOSE_PRICE_INDEX,
        slow_type="EMA", fast_type="EMA", slow_column_index=CLOSE_PRICE_INDEX,
    )

    atr_indicator = ATRIndicator()

    backtest_strategy(
        symbol="BTCUSDT",
        interval="15m",
        market="FUTURES",
        db_path="data/binance_candles.db",
        skip=256,
        trade_ratio=0.85,
        start_cash=1000,
        maker_fee_rate=0.0002,
        taker_fee_rate=0.0004,
        leverage=1,
        strategy_type=IndicatorStrategy,
        indicators=[ma_price_ind, ha_ind],
        exit_indicators=[ha_exit_ind],
        candlestick_type=CandlestickType.HEIKIN_ASHI,
        extra_plots=[
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
