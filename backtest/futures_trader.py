import copy
from typing import Callable, Optional, Iterable, List

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


ENTRY_TIME_INDEX = 0
ENTRY_PRICE_INDEX = 1
ENTRY_QUANTITY_INDEX = 2
ENTRY_SIDE_INDEX = 3
ENTRY_LEVERAGE_INDEX = 4
EXIT_TIME_INDEX = 5
EXIT_PRICE_INDEX = 6
EXIT_PROFIT_INDEX = 7


class BacktestPosition:
    __slots__ = ("entry_time", "entry_price", "entry_quantity", "entry_leverage", "exit_time", "exit_price")

    def __init__(self, entry_time: int, entry_price: float, entry_quantity: float, entry_leverage: int):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.entry_quantity = entry_quantity
        self.entry_leverage = entry_leverage
        self.exit_time: Optional[int] = None
        self.exit_price: Optional[float] = None

    @property
    def side(self):
        return BUY if self.entry_quantity > 0 else SELL

    def set_exit(self, time: int, price: float):
        self.exit_time = time
        self.exit_price = price

    @property
    def exit_profit(self):
        return (self.exit_price - self.entry_price) * self.entry_quantity * self.entry_leverage


def create_position_array(positions: Iterable[BacktestPosition]):
    return np.array([
        tuple(position.entry_time for position in positions),
        tuple(position.entry_price for position in positions),
        tuple(position.entry_quantity for position in positions),
        tuple(position.side for position in positions),
        tuple(position.entry_leverage for position in positions),
        tuple(position.exit_time for position in positions),
        tuple(position.exit_price for position in positions),
        tuple(position.exit_profit for position in positions),
    ])


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
        BacktestFuturesTrader class

        :param client: Broker client
        :param interval:
        :param trade_ratio: Trade ratio, between 0 and 1
        :param balance:
        :param fee_ratio:
        :param leverage:

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
                    entry_time=open_time,
                    entry_quantity=self.limit_order.quantity,
                    entry_leverage=self._leverage,
                    entry_price=self.limit_order.price,
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
                # print(
                #     "WARNING: Both take profit and loss has been hit in the same iteration!"
                # )
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
            if order.type == "TAKE_PROFIT_MARKET":
                self.take_profit_order = None
            else:
                self.stop_order = None

            self.__close_position(time=exit_time, price=order.stop_price)

    def cancel_orders(self, symbol: str):
        self.limit_order = None
        self.take_profit_order = None
        self.stop_order = None

    def create_orders(self, *orders: Order):
        for order in orders:
            if order.type == "MARKET":
                latest_candle = self.candles[-1]
                self.position = BacktestPosition(
                    entry_time=latest_candle[OPEN_TIME_INDEX],
                    entry_quantity=order.quantity,
                    entry_leverage=self._leverage,
                    entry_price=latest_candle[CLOSE_PRICE_INDEX],
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

    def close_position(self):
        latest_candle = self.candles[-1]
        close_time = latest_candle[OPEN_TIME_INDEX] + self._interval
        close_price = latest_candle[CLOSE_PRICE_INDEX]
        self.__close_position(time=close_time, price=close_price)

    def __close_position(self, time, price):
        if self.position is not None:
            self.position.set_exit(time=time, price=price)
            self.balance += self.position.exit_profit
            self.positions.append(self.position)
            self.position = None

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
