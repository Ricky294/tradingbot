from trader.core.model import SymbolInfo
from trader.core.enum import CandlestickType
from trader.backtest.plot import Plot

from backtest.strategy_runner import backtest_strategy
from indicator.signal import HeikinAshiIndicator, DMIIndicator
from strategy import IndicatorStrategy


if __name__ == "__main__":

    start_cash = 1000

    upper_limit = 70
    lower_limit = 30

    dmi_ind = DMIIndicator()
    ha_ind = HeikinAshiIndicator()

    ha_exit = HeikinAshiIndicator()

    backtest_strategy(
        symbol_info=SymbolInfo(symbol="BTCUSDT", price_precision=2, quantity_precision=3),
        interval="15m",
        market="FUTURES",
        db_path="data/binance_candles.db",
        skip=256,
        trade_ratio=0.85,
        start_cash=1000,
        leverage=1,
        strategy_type=IndicatorStrategy,
        indicators=[dmi_ind, ha_ind],
        exit_indicators=[ha_exit],
        candlestick_type=CandlestickType.LINE,
        extra_plots=[
            Plot(
                number=3,
                type="scatter",
                data_callback=dmi_ind,
                params=[
                    dict(
                        y=DMIIndicator.ADX_INDEX,
                        name="ADX",
                        line=dict(
                            width=2,
                            color="black",
                        )
                    ),
                    dict(
                        y=DMIIndicator.PLUS_DI_INDEX,
                        name="Plus DI",
                        line=dict(
                            width=1.25,
                            color="green",
                        )
                    ),
                    dict(
                        y=DMIIndicator.MINUS_DI_INDEX,
                        name="Plus DI",
                        line=dict(
                            width=1.25,
                            color="red",
                        )
                    ),
                ]
            )
        ]
    )
