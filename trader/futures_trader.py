from typing import List

from binance.client import Client

from model.balance import Balance
from model.order import Order
from binance_.futures import (
    create_futures_batch_orders,
    create_futures_position_closing_order,
    cancel_futures_symbol_orders,
)
from model.position import Position


class TradeError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Trader:
    def __init__(self, client: Client, market: str, ratio: float):
        """
        :param client: Broker client
        :param ratio: Trade ratio, between 0 and 1

        Note: Try to avoid ratio values close to 0 or 1.
        """
        self.market = str(market)
        if ratio <= 0.0 or ratio >= 1.0:
            raise TradeError("'ratio' must be between 0 and 1")

        self.client = client
        self.ratio = ratio

    def cancel_orders(self, symbol: str) -> List[Order]:
        return cancel_futures_symbol_orders(client=self.client, symbol=symbol)

    def close_position(self, position: Position) -> Order:
        return create_futures_position_closing_order(self.client, position)

    def create_orders(self, *orders: Order) -> List[Order]:
        return create_futures_batch_orders(self.client, *orders)

    def create_orders_by_ratio(self, balance: Balance, *orders: Order) -> List[Order]:
        """
        Automatically calculates order quantities based on self.ratio number and balance parameter.
        """

        # TODO: Implementation

        return create_futures_batch_orders(self.client, *orders)
