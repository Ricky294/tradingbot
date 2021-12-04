from typing import List, Callable, Dict

import pandas as pd

from abstract import FuturesTrader
from backtest import BacktestClient
from model import Balance, Order, Position


class TradeError(Exception):
    def __init__(self, msg):
        self.msg = msg


class BacktestFuturesTrader(FuturesTrader, Callable):
    def __init__(self, client: BacktestClient, ratio: float):
        """
        :param client: Broker client
        :param ratio: Trade ratio, between 0 and 1

        Note: Try to avoid ratio values close to 0 or 1.
        """
        super().__init__(ratio)
        self.client = client
        self.candles: Dict[str, pd.DataFrame]

    def __call__(self, candles: Dict[str, pd.DataFrame]):
        self.candles = candles

    def cancel_orders(self, symbol: str) -> List[Order]:
        pass

    def create_position_close_order(self, position: Position) -> Order:
        pass

    def create_orders(self, *orders: Order) -> List[Order]:
        pass

    def create_orders_by_ratio(self, balance: Balance, *orders: Order) -> List[Order]:
        pass

    def get_balances(self):
        pass

    def get_open_orders(self, symbol: str):
        pass

    def get_symbol_info(self, symbol: str):
        pass

    def get_position(self, symbol: str):
        pass

    def set_leverage(self, symbol: str, leverage: int):
        pass
