from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from model import Position, Order, Balance, SymbolInfo


class TradeError(Exception):
    def __init__(self, msg):
        self.msg = msg


class FuturesTrader(ABC):
    def __init__(self, trade_ratio: float):
        if trade_ratio <= 0.0 or trade_ratio >= 1.0:
            raise TradeError("'ratio' must be between 0 and 1")

        self.trade_ratio = trade_ratio

    @abstractmethod
    def cancel_orders(self, symbol: str) -> List[Order]: ...

    @abstractmethod
    def create_orders(self, *orders: Order) -> List[Order]: ...

    @abstractmethod
    def close_position(self): ...

    @abstractmethod
    def get_balances(self) -> Dict[str, Balance]: ...

    @abstractmethod
    def get_open_orders(self, symbol: str) -> List[Order]: ...

    @abstractmethod
    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]: ...

    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]: ...

    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> None: ...

    @abstractmethod
    def get_leverage(self, symbol) -> int: ...
