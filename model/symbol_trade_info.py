from typing import List, Optional

from model import Order, Position, SymbolInfo


class SymbolTradeInfo:
    __slots__ = ("orders", "symbol_info", "position")

    def __init__(
        self, orders: List[Order], symbol_info: SymbolInfo, position: Optional[Position]
    ):
        self.orders = orders
        self.symbol_info = symbol_info
        self.position = position

    @property
    def symbol(self):
        return self.symbol_info.symbol
