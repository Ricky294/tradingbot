import copy
from typing import Callable, Optional, List, Union

import numpy as np

from binance.client import Client

from abstract import FuturesTrader
from backtest.position import BacktestPosition
from consts.actions import SELL, BUY
from consts.candle_column_index import *
from consts.order import LIMIT_ORDER, MARKET_ORDER
from model import Balance, SymbolInfo
from model.order import LimitOrder, MarketOrder, TakeProfitMarketOrder, StopLossMarketOrder
from util.common import interval_to_seconds


class BacktestFuturesTrader(FuturesTrader, Callable):
    def __init__(
        self,
        client: Client,
        interval: str,
        trade_ratio: float,
        balance: Balance = Balance("USDT", total=1_000, available=1_000),
        fee_ratio=0.001,
        leverage=1,
    ):
        super().__init__(trade_ratio)
        self.fee_ratio = fee_ratio
        self.client = client
        self._interval = interval_to_seconds(interval)

        self._leverage = leverage

        self.symbol_info = self._get_all_symbol_info()

        self.initial_balance = copy.deepcopy(balance)
        self.balance = balance

        self.positions: List[BacktestPosition] = []
        self.position: Optional[BacktestPosition] = None

        self.market_order: Optional[MarketOrder] = None
        self.stop_order: Optional[StopLossMarketOrder] = None
        self.take_profit_order: Optional[TakeProfitMarketOrder] = None
        self.limit_order: Optional[LimitOrder] = None

        self.latest_open_time: float
        self.latest_high_price: float
        self.latest_low_price: float
        self.latest_close_price: float

    def _is_limit_buy_hit(self):
        return (
            self.limit_order.side == BUY
            and self.latest_low_price < self.limit_order.price
        )

    def _is_limit_sell_hit(self):
        return (
            self.limit_order.side == SELL
            and self.latest_high_price > self.limit_order.price
        )

    def _is_stop_loss_hit(self):
        if self.stop_order is None:
            return False

        return (
            self.latest_high_price > self.stop_order.stop_price
            if self.position.side == SELL
            else self.latest_low_price < self.stop_order.stop_price
        )

    def _is_take_profit_hit(self):
        if self.take_profit_order is None:
            return False

        return (
            self.latest_high_price > self.take_profit_order.stop_price
            if self.position.side == BUY
            else self.latest_low_price < self.take_profit_order.stop_price
        )

    def _create_position(self, price: float, quantity: float):
        self.position = BacktestPosition(
            entry_time=self.latest_open_time,
            entry_price=price,
            entry_quantity=quantity,
            leverage=self._leverage,
        )
        self.balance.available -= price * abs(quantity)

    def _adjust_position(self, price: float, quantity: float):
        self.position.adjust(
            time=self.latest_open_time,
            price=price,
            quantity=quantity,
        )

        if self.position.is_closed():
            self.balance.total += self.position.calculate_profit(price)
            self.balance.available = self.balance.total
            self.positions.append(self.position)
            self.position = None
        else:
            self.balance.available += price * quantity

    def get_limit_order(self):
        return self.limit_order

    def get_take_profit_order(self):
        return self.take_profit_order

    def get_stop_loss_order(self):
        return self.stop_order

    def create_or_adjust_position(self, price: float, quantity: float):
        if self.position is None:
            self._create_position(
                price=price,
                quantity=quantity,
            )
        else:
            self._adjust_position(
                price=price,
                quantity=quantity,
            )

    def __call__(self, candles: np.ndarray):
        latest_candle = candles[-1]
        self.latest_open_time = latest_candle[OPEN_TIME_INDEX]
        self.latest_high_price = latest_candle[HIGH_PRICE_INDEX]
        self.latest_low_price = latest_candle[LOW_PRICE_INDEX]
        self.latest_close_price = latest_candle[CLOSE_PRICE_INDEX]

        just_entered = False
        if self.market_order is not None:
            self.create_or_adjust_position(
                price=self.latest_close_price,
                quantity=self.market_order.quantity,
            )
            self.market_order = None
            just_entered = True

        if self.limit_order is not None:
            if self._is_limit_sell_hit() or self._is_limit_buy_hit():
                self.create_or_adjust_position(
                    price=self.limit_order.price,
                    quantity=self.limit_order.quantity,
                )

                self.limit_order = None
                just_entered = True

        if self.position is not None and not just_entered:
            take_profit_hit = self._is_take_profit_hit()
            stop_hit = self._is_stop_loss_hit()

            if take_profit_hit and stop_hit:
                rand_choice = np.round(np.random.rand())
                if rand_choice == 1:
                    take_profit_hit = False
            if take_profit_hit:
                self._close_position(self.take_profit_order.stop_price)
                self.take_profit = None
                self.stop_order = None
            elif stop_hit:
                self._close_position(self.stop_order.stop_price)
                self.take_profit = None
                self.stop_order = None

                if self.balance.total <= 0:
                    from backtest import NotEnoughFundsError
                    raise NotEnoughFundsError(
                        f"You got liquidated! Final balance: {self.balance}"
                    )

    def cancel_orders(self, symbol: str):
        self.limit_order = None
        self.take_profit_order = None
        self.stop_order = None

    def cancel_limit_order(self, symbol: str):
        self.limit_order = None

    def cancel_take_profit_order(self, symbol: str):
        self.take_profit_order = None

    def cancel_stop_loss_orders(self, symbol: str):
        self.stop_order = None

    def create_position(
            self,
            order: Union[MarketOrder, LimitOrder],
            take_profit_order: Optional[TakeProfitMarketOrder] = None,
            stop_loss_order: Optional[StopLossMarketOrder] = None,
    ):
        if order.type == MARKET_ORDER:
            self.market_order = order
        elif order.type == LIMIT_ORDER:
            self.limit_order = order

        self.take_profit_order = take_profit_order
        self.stop_order = stop_loss_order

    def _close_position(self, price: float):
        if self.position is not None:
            self.position.close(
                time=self.latest_open_time,
                price=price,
            )
            self.balance.total += self.position.calculate_profit(price)
            self.balance.available = self.balance.total
            self.positions.append(self.position)
            self.position = None

    def close_position(self):
        self._close_position(self.latest_close_price)

    def get_balances(self):
        return {"USDT": self.balance}

    def get_open_orders(self, symbol: str):
        open_orders = []
        if self.limit_order is not None:
            open_orders.append(self.limit_order)
        elif self.take_profit_order is not None:
            open_orders.append(self.take_profit_order)
        elif self.stop_order is not None:
            open_orders.append(self.stop_order)
        return open_orders

    def _get_all_symbol_info(self):
        exchange_info: dict = self.client.futures_exchange_info()
        return {
            symbol_info["symbol"]: SymbolInfo(**symbol_info)
            for symbol_info in exchange_info["symbols"]
        }

    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        symbol = symbol.upper()

        return self.symbol_info[symbol]

    def get_position(self, symbol: str) -> Optional[BacktestPosition]:
        return self.position

    def set_leverage(self, symbol: str, leverage: int):
        self._leverage = leverage

    def get_leverage(self, symbol) -> int:
        return self._leverage
