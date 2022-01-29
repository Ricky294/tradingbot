from backtest.strategy_runner import TradeVariable, backtest_multiple_strategy
from shared.const.candle_index import *
from indicator.signal import RSIIndicator, DoubleMATrendIndicator
from indicator.sltp import ATRIndicator

from plot import Plot

from strategy import IndicatorStrategy


def create_rsi_and_ma_trend_indicator(
        upper_limit: float,
        lower_limit: float,
        slow_period: int,
        fast_period: int,
        slow_type: str,
        fast_type: str,
):
    rsi_ind = RSIIndicator(upper_limit=upper_limit, lower_limit=lower_limit)
    ma_trend_ind = DoubleMATrendIndicator(
        slow_period=slow_period, fast_period=fast_period, fast_column_index=CLOSE_PRICE_INDEX,
        slow_type=slow_type, fast_type=fast_type, slow_column_index=CLOSE_PRICE_INDEX,
    )

    return rsi_ind, ma_trend_ind


def extra_plots(rsi_ind: RSIIndicator, ma_trend_ind: DoubleMATrendIndicator):
    return [
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
                ),
            ],
        ),
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
    ]


if __name__ == "__main__":

    ind_1 = create_rsi_and_ma_trend_indicator(70, 30, 200, 50, "EMA", "SMA")
    ind_2 = create_rsi_and_ma_trend_indicator(80, 20, 200, 50, "SMA", "EMA")
    ind_3 = create_rsi_and_ma_trend_indicator(70, 30, 200, 50, "EMA", "EMA")

    atr_ind = ATRIndicator()

    backtest_multiple_strategy(
        symbol="BTCUSDT",
        market="FUTURES",
        db_path="data/binance_candles.db",
        skip=256,
        start_cash=1000,
        strategy_type=IndicatorStrategy,
        extra_plots_callback=extra_plots,
        variables=[
            TradeVariable(
                indicators=ind_1,
                sltp_indicator=atr_ind,
                interval="15m",
                leverage=1,
                trade_ratio=0.05,
            ),
            TradeVariable(
                indicators=ind_2,
                sltp_indicator=atr_ind,
                interval="15m",
                leverage=1,
                trade_ratio=0.05,
            ),
            TradeVariable(
                indicators=ind_3,
                sltp_indicator=atr_ind,
                interval="15m",
                leverage=1,
                trade_ratio=0.05,
            ),
        ]
    )
