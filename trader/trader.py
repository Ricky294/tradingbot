from typing import List

from binance.client import Client

from indicator.indicator import Indicator
from model.order import Order, OrderSide
from binance_.futures import create_futures_order


class TradeError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Trader:
    def __init__(self, client: Client, indicator: Indicator, percentage: float):
        """
        :param client: Broker client
        :param indicator: Signals buy or sell
        :param percentage: Trade percentage, between 0 and 1

        Note: Try to avoid percentage values very close to 0 or 1.
        """
        if percentage <= 0.0 or percentage >= 1.0:
            raise TradeError("'percentage' must be between 0 and 1")

        self.client = client
        self.indicator = indicator
        self.percentage = percentage
        self.signal = indicator.signal_enum()

    def create_orders_on_buy_signal(self, *orders: Order) -> List[Order]:
        if self.signal is OrderSide.BUY:
            return [
                create_futures_order(client=self.client, order=order)
                for order in orders
            ]
        return []

    def create_orders_on_sell_signal(self, *orders: Order) -> List[Order]:
        if self.signal is OrderSide.SELL:
            return [
                create_futures_order(client=self.client, order=order)
                for order in orders
            ]
        return []
