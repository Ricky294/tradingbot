from typing import List

import numpy as np

from trader.core.interface import FuturesTrader
from trader.core.const.candle_index import CLOSE_PRICE_INDEX
from trader.core.const.trade_actions import NONE, BUY, SELL
from trader.core.strategy import Strategy
from trader.core.util.trade import calculate_quantity

from indicator.signal import Indicator
from indicator.sltp import SLTPIndicator
from util import is_empty


class IndicatorStrategy(Strategy):

    def __init__(
            self,
            symbol: str,
            trader: FuturesTrader,
            indicators: List[Indicator],
            trade_ratio: float,
            leverage: int,
            sltp_indicator: SLTPIndicator = None,
            exit_indicators: List[Indicator] = None,
            can_change_position=False,
            asset="USDT",
    ):
        if sltp_indicator is None and is_empty(exit_indicators):
            raise ValueError(
                "sltp_indicator and exit_indicator are both None. "
                "Provide at least one of them to allow the system to close positions."
            )

        super().__init__(trader=trader)
        self.symbol = symbol
        self.trade_ratio = trade_ratio
        self.asset = asset
        self.leverage = leverage
        self.indicators = indicators
        self.exit_indicators = exit_indicators
        self.sltp_indicator = sltp_indicator
        self.can_change_position = can_change_position

    def __indicator_signal(self, candles: np.ndarray, indicators: List[Indicator]):
        signals = tuple(indicator.signal(candles) for indicator in indicators)
        if all(tuple(signal == BUY for signal in signals)):
            return BUY
        elif all(tuple(signal == SELL for signal in signals)):
            return SELL
        return NONE

    def on_candle(self, candles: np.ndarray):
        signal = self.__indicator_signal(candles, self.indicators)

        position = self.trader.get_position(self.symbol)
        entry_signal = signal != NONE and (position is None or self.can_change_position)

        if entry_signal:
            latest_close = candles[-1][CLOSE_PRICE_INDEX]

            quantity = calculate_quantity(
                side=signal,
                price=latest_close,
                trade_ratio=self.trade_ratio,
                leverage=self.leverage,
                balance=self.trader.get_balance(self.asset).available
            )

            stop_loss_price, take_profit_price = None, None

            if self.sltp_indicator is not None:
                stop_loss_price, take_profit_price = self.sltp_indicator(
                    candles,
                    side=signal,
                    leverage=self.trader.get_leverage(self.symbol)
                )

            orders = self.trader.create_position(
                symbol=self.symbol,
                quantity=quantity,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
            )

        elif position is not None and not is_empty(self.exit_indicators):
            exit_signal = self.__indicator_signal(candles, self.exit_indicators)

            if (exit_signal == BUY and position.side == SELL) or (exit_signal == SELL and position.side == BUY):
                self.trader.close_position(self.symbol)
