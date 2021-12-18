from abc import abstractmethod

import pandas as pd

from typing import Dict, Union, Callable

from binance.client import Client
from crypto_data.binance.candle import StreamCandle

from abstract import FuturesTrader
from indicator import Indicator
from strategy import SingleSymbolStrategy, MultiSymbolStrategy
from util import get_object_from_module


def create_indicators(indicators_config: Dict[str, Dict]) -> Dict[str, Indicator]:
    indicators = {
        name: get_object_from_module(
            module_name="indicator", object_name=indicator.pop("type")
        )(**indicator)
        for name, indicator in indicators_config.items()
    }

    return indicators


def create_backtest_indicators(
    indicators_config: Dict[str, Dict], candles: pd.DataFrame, skip: int
) -> Dict[str, Indicator]:
    from backtest import BacktestIndicator

    indicators = create_indicators(indicators_config)

    return {
        name: BacktestIndicator(ind, candles, skip) for name, ind in indicators.items()
    }


def create_strategy(
    strategy_config: Dict[str, any], trader: FuturesTrader, **indicators
) -> Union[SingleSymbolStrategy, MultiSymbolStrategy]:
    strategy_class = get_object_from_module(
        module_name="strategy", object_name=strategy_config.pop("type")
    )

    return strategy_class(**strategy_config, trader=trader, **indicators)


class StrategyRunner:
    @classmethod
    def from_multi_symbol(
        cls,
        strategy: MultiSymbolStrategy,
        candles: Dict[str, pd.DataFrame],
        interval: str,
        market: str,
    ):
        return cls(
            strategy=strategy,
            candles=candles,
            interval=interval,
            market=market,
        )

    @classmethod
    def from_single_symbol(
        cls,
        strategy: SingleSymbolStrategy,
        candles: pd.DataFrame,
        interval: str,
        market: str,
    ):
        return cls(
            strategy=strategy,
            candles=candles,
            interval=interval,
            market=market,
        )

    def __init__(
        self,
        strategy: Union[SingleSymbolStrategy, MultiSymbolStrategy],
        candles: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        interval: str,
        market: str,
    ):
        self.strategy = strategy
        self.candles = candles
        self.interval = interval
        self.market = str(market).upper()

    @abstractmethod
    def run(self):
        pass


class BacktestRunner(StrategyRunner):
    @classmethod
    def from_config(cls, config: Dict[str, any], candles: pd.DataFrame, skip: int = 0):
        from backtest import BacktestFuturesTrader

        client = Client()
        trader = BacktestFuturesTrader(
            client=client, interval=config["interval"], **config["trader"]
        )

        backtest_indicators = create_backtest_indicators(
            config["indicators"], candles=candles, skip=skip
        )
        strategy = create_strategy(
            config["strategy"], trader=trader, **backtest_indicators
        )

        interval = config["interval"]
        market = config["market"]

        return cls(
            strategy=strategy,
            candles=candles,
            interval=interval,
            market=market,
        )

    def run(self, skip: int = 0):
        from backtest import backtest_candle_stream, backtest_candle_multi_stream

        if isinstance(self.strategy, SingleSymbolStrategy):
            backtest_candle_stream(
                strategy=self.strategy,
                trader=self.strategy.trader,
                candles=self.candles,
                skip=skip,
            )
        elif isinstance(self.strategy, MultiSymbolStrategy):
            backtest_candle_multi_stream(
                strategy=self.strategy,
                trader=self.strategy.trader,
                symbol_candles_dict=self.candles,
                skip=skip,
            )
        else:
            raise ValueError(
                "strategy must be an instance of SingleSymbolStrategy or MultiSymbolStrategy"
            )


class BinanceRunner:
    @classmethod
    def from_config(
        cls,
        config: Dict[str, any],
        candles: pd.DataFrame,
        api_key: str,
        api_secret: str,
    ):
        from binance_ import BinanceFuturesTrader
        from binance.client import Client

        client = Client(api_key=api_key, api_secret=api_secret)
        trader = BinanceFuturesTrader(client=client, **config["trader"])

        indicators = create_indicators(config["indicators"])
        strategy = create_strategy(config["strategy"], trader=trader, **indicators)
        interval = config["interval"]
        market = config["market"]

        return cls(
            strategy=strategy,
            candles=candles,
            interval=interval,
            market=market,
        )

    def __init__(
        self,
        strategy: Union[SingleSymbolStrategy, MultiSymbolStrategy],
        candles: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        interval: str,
        market: str,
    ):
        self.strategy = strategy
        self.candles = candles
        self.interval = interval
        self.market = str(market).upper()

    def run(self, on_candle: Callable[[StreamCandle], None]):
        from crypto_data.binance.stream import candle_stream, candle_multi_stream

        if isinstance(self.strategy, SingleSymbolStrategy):
            candle_stream(
                symbol=self.strategy.symbol,
                interval=self.interval,
                market=self.market,
                candles=self.candles,
                on_candle=on_candle,
                on_candle_close=self.strategy,
            )

        elif isinstance(self.strategy, MultiSymbolStrategy):
            candle_multi_stream(
                interval=self.interval,
                market=self.market,
                symbol_candles=self.candles,
                on_candle=on_candle,
                on_candle_close=self.strategy,
            )
