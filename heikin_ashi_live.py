from live.strategy_runner import run_binance_strategy
from indicator.signal import HeikinAshiIndicator

from strategy import IndicatorStrategy
from trader.core.util.common import read_json

if __name__ == "__main__":

    ha_ind = HeikinAshiIndicator()
    ha_exit_ind = HeikinAshiIndicator()

    symbol = "BTCUSDT"
    interval = "15m"
    market = "FUTURES"
    leverage = 1
    trade_ratio = 0.6

    run_binance_strategy(
        symbol=symbol,
        interval=interval,
        market=market,
        trade_ratio=trade_ratio,
        leverage=leverage,
        db_path="data/binance_candles.db",
        strategy_type=IndicatorStrategy,
        indicators=[ha_ind],
        exit_indicators=[ha_exit_ind],
        **read_json("secrets/binance_secrets.json")
    )
