import copy
from typing import List, Callable, Optional

import numpy as np

from binance.client import Client

from abstract import FuturesTrader
from consts.actions import SELL, BUY
from consts.candle_column_index import *
from model import Balance, Order, SymbolInfo
from util.common import interval_to_seconds


class TradeError(Exception):
    def __init__(self, msg):
        self.msg = msg


class NotEnoughFundsError(Exception):
    def __init__(self, msg):
        self.msg = msg


class BacktestPosition:
    __slots__ = ("time", "price", "quantity", "leverage", "exit_time", "exit_price")

    def __init__(self, time: int, price: float, quantity: float, leverage: int):
        self.time = time
        self.price = price
        self.quantity = quantity
        self.leverage = leverage
        self.exit_time: Optional[int] = None
        self.exit_price: Optional[float] = None

    @property
    def side(self):
        return BUY if self.quantity > 0 else SELL

    def set_exit(self, time: int, price: float):
        self.exit_time = time
        self.exit_price = price

    @property
    def exit_profit(self):
        return (self.exit_price - self.price) * self.quantity * self.leverage


def _is_limit_buy_hit(order: Order, low_price: float):
    return order.side == BUY and low_price < order.price


def _is_limit_sell_hit(order: Order, high_price: float):
    return order.side == SELL and high_price > order.price


def _is_stop_loss_hit(
        order: Order,
        position: BacktestPosition,
        high_price: float,
        low_price: float
):
    return (
        high_price > order.stop_price
        if position.side == SELL
        else low_price < order.stop_price
    )


def _is_take_profit_hit(
    order: Order, position: BacktestPosition, high_price: float, low_price: float
):
    return (
        high_price > order.stop_price
        if position.side == BUY
        else low_price < order.stop_price
    )


class BacktestFuturesTrader(FuturesTrader, Callable):
    def __init__(
        self,
        client: Client,
        interval: str,
        trade_ratio: float,
        balance: Balance = Balance("USDT", balance=1_000, free=1_000),
        fee_ratio=0.001,
        leverage=1,
    ):
        """
        :param client: Broker client
        :param trade_ratio: Trade ratio, between 0 and 1

        Note: Try to avoid ratio values close to 0 or 1.
        """
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

        self.take_profit_order: Optional[Order] = None
        self.stop_order: Optional[Order] = None
        self.limit_order: Optional[Order] = None

    def __call__(self, candles: np.ndarray):
        self.candles = candles
        latest_candle = candles[-1]
        high_price = latest_candle[HIGH_PRICE_INDEX]
        low_price = latest_candle[LOW_PRICE_INDEX]
        open_time = latest_candle[OPEN_TIME_INDEX]

        if self.position is None and self.limit_order is not None:

            if _is_limit_sell_hit(
                self.limit_order, high_price=high_price
            ) or _is_limit_buy_hit(self.limit_order, low_price=low_price):
                self.position = BacktestPosition(
                    time=open_time,
                    quantity=self.limit_order.quantity,
                    leverage=self._leverage,
                    price=self.limit_order.price,
                )
                self.limit_order = None

        elif self.position is not None:
            close_price = latest_candle[CLOSE_PRICE_INDEX]
            open_price = latest_candle[OPEN_PRICE_INDEX]

            tp_hit = self.take_profit_order is not None and _is_take_profit_hit(
                order=self.take_profit_order,
                position=self.position,
                high_price=high_price,
                low_price=low_price,
            )

            sl_hit = self.stop_order is not None and _is_stop_loss_hit(
                order=self.stop_order,
                position=self.position,
                high_price=high_price,
                low_price=low_price,
            )

            exit_time = open_time + self._interval
            if tp_hit and sl_hit:
                print(
                    "WARNING: Both take profit and loss has been hit in the same iteration!"
                )
                is_bullish_candle = close_price > open_price
                if (is_bullish_candle and self.position.side == BUY) or (
                    not is_bullish_candle and self.position.side == SELL
                ):
                    self._take_profit_or_loss(self.take_profit_order, exit_time)
                else:
                    self._take_profit_or_loss(self.stop_order, exit_time)
            elif tp_hit:
                self._take_profit_or_loss(self.take_profit_order, exit_time)
            elif sl_hit:
                self._take_profit_or_loss(self.stop_order, exit_time)
                if self.balance <= 0:
                    raise NotEnoughFundsError(
                        f"You got liquidated! Final balance: {self.balance}"
                    )

    def _take_profit_or_loss(self, order: Order, exit_time: int):
        if self.position is not None:
            self.position.set_exit(time=exit_time, price=order.stop_price)
            self.balance += self.position.exit_profit
            if order.type == "TAKE_PROFIT_MARKET":
                self.take_profit_order = None
            else:
                self.stop_order = None

            self.positions.append(self.position)
            self.position = None

    def cancel_orders(self, symbol: str):
        self.limit_order = None
        self.take_profit_order = None
        self.stop_order = None

    def create_orders(self, *orders: Order):
        for order in orders:
            if order.type == "MARKET":
                latest_candle = self.candles[-1]
                self.position = BacktestPosition(
                    time=latest_candle[OPEN_TIME_INDEX],
                    quantity=order.quantity,
                    leverage=self._leverage,
                    price=latest_candle[CLOSE_PRICE_INDEX],
                )
            elif order.type == "LIMIT":
                latest_close = self.candles[-1][CLOSE_PRICE_INDEX]
                if (order.side == BUY and order.price >= latest_close) or (
                    order.side == SELL and order.price <= latest_close
                ):
                    raise ValueError(
                        "Incorrect order price. Order would immediately triggered."
                    )
                self.limit_order = order
            elif order.type == "TAKE_PROFIT_MARKET":
                self.take_profit_order = order
            elif order.type == "STOP_MARKET":
                self.stop_order = order

    def get_balances(self):
        return {"USDT": self.balance}

    def get_open_orders(self, symbol: str):
        orders = []
        if self.limit_order is not None:
            orders.append(self.limit_order)
        if self.take_profit_order is not None:
            orders.append(self.take_profit_order)
        if self.stop_order is not None:
            orders.append(self.stop_order)
        return orders

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
