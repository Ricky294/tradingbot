from backtest.helper import TradeVariable, run_multiple_backtest
from consts.candle_index import *
from indicator.ma_trend import MATrendIndicator
from indicator.mixed.rsi_with_ma_trend import RSIWithMATrendIndicator

from indicator import RSIIndicator
from plot import Plot

from strategy import IndicatorStrategy


def create_rsi_with_ma_trend_indicator(
        upper_limit: float,
        lower_limit: float,
        slow_period: int,
        fast_period: int,
        slow_type: str,
        fast_type: str,
):
    rsi_ind = RSIIndicator(upper_limit=upper_limit, lower_limit=lower_limit)
    ma_trend_ind = MATrendIndicator(
        slow_period=slow_period, fast_period=fast_period, fast_column_index=CLOSE_PRICE_INDEX,
        slow_type=slow_type, fast_type=fast_type, slow_column_index=CLOSE_PRICE_INDEX,
    )

    return RSIWithMATrendIndicator(rsi=rsi_ind, ma_trend=ma_trend_ind)


def extra_plots(indicator: RSIWithMATrendIndicator):
    return [
        Plot(
            number=2,
            type="scatter",
            data_callback=indicator,
            params=[
                dict(
                    y=RSIWithMATrendIndicator.SLOW_MA_INDEX,
                    name="Slow MA",
                    opacity=0.8,
                    line=dict(
                        width=2,
                        color="red",
                    )
                ),
                dict(
                    y=RSIWithMATrendIndicator.FAST_MA_INDEX,
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
            data_callback=indicator,
            params=[
                dict(
                    y=RSIWithMATrendIndicator.RSI_INDEX,
                    name="RSI",
                ),
                dict(
                    constant_y=indicator.rsi.upper_limit,
                    name="Upper RSI",
                    marker={"color": "blue"},
                ),
                dict(
                    constant_y=indicator.rsi.lower_limit,
                    name="Lower RSI",
                    marker={"color": "blue"},
                ),
            ]
        ),
    ]


if __name__ == "__main__":

    ind_1 = create_rsi_with_ma_trend_indicator(70, 30, 200, 50, "EMA", "SMA")
    ind_2 = create_rsi_with_ma_trend_indicator(80, 20, 200, 50, "SMA", "EMA")
    ind_3 = create_rsi_with_ma_trend_indicator(70, 30, 200, 50, "EMA", "EMA")

    run_multiple_backtest(
        symbol="BTCUSDT",
        market="FUTURES",
        db_path="data/binance_candles.db",
        skip=256,
        start_cash=1000,
        strategy_type=IndicatorStrategy,
        extra_plots_callback=extra_plots,
        variables=[
            TradeVariable(
                indicator=ind_1,
                interval="15m",
                leverage=1,
                trade_ratio=0.85,
            ),
            TradeVariable(
                indicator=ind_2,
                interval="15m",
                leverage=1,
                trade_ratio=0.85,
            ),
            TradeVariable(
                indicator=ind_3,
                interval="15m",
                leverage=1,
                trade_ratio=0.85,
            ),
        ]
    )
