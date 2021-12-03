from abc import ABC, abstractmethod
from typing import List, Optional

from model import Position, Order, Balance, SymbolInfo


class TradeError(Exception):
    def __init__(self, msg):
        self.msg = msg


class FuturesTrader(ABC):
    def __init__(self, ratio: float):
        if ratio <= 0.0 or ratio >= 1.0:
            raise TradeError("'ratio' must be between 0 and 1")

        self.ratio = ratio

    @abstractmethod
    def cancel_orders(self, symbol: str) -> List[Order]:
        pass

    @abstractmethod
    def create_position_close_order(self, position: Position) -> Order:
        pass

    @abstractmethod
    def create_orders(self, *orders: Order) -> List[Order]:
        pass

    @abstractmethod
    def create_orders_by_ratio(self, balance: Balance, *orders: Order) -> List[Order]:
        pass

    @abstractmethod
    def get_balances(self) -> List[Balance]:
        pass

    @abstractmethod
    def get_open_orders(self, symbol: str) -> List[Order]:
        pass

    @abstractmethod
    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        pass

    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]:
        pass

    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int):
        pass
