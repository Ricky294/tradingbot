from typing import Dict, List, Optional, Union
from binance.client import Client

from abstract import FuturesTrader
from model import Order, TimeInForce, Balance, Position, SymbolInfo


class BinanceFuturesTrader(FuturesTrader):
    def __init__(self, client: Client, ratio: float):
        """
        :param client: Broker client
        :param ratio: Trade ratio, between 0 and 1

        Note: Try to avoid ratio values close to 0 or 1.
        """
        super().__init__(ratio)
        self.client = client

    def create_orders_by_ratio(self, balance: Balance, *orders: Order) -> List[Order]:
        # self.ratio
        # TODO: Implementation
        pass

    def create_orders(self, *orders: Order) -> List[Order]:
        """
        Creates multiple order at the same time (all fails or all gets created)
        Limitations: Binance can only create max. 5 orders in a batch
        """

        orders = {"batchOrders": [order.to_binance_order() for order in orders]}
        binance_orders = self.client.futures_place_batch_order(**orders)

        return [Order.from_binance(order) for order in binance_orders]

    def create_order(self, order: Order) -> Order:
        order = self.client.futures_create_order(**order.to_binance_order())
        return Order.from_binance(order)

    def create_position_close_order(
        self,
        position: Position,
        price: float = None,
        time_in_force: Union[str, TimeInForce] = "GTC",
    ) -> Order:
        """
        Creates an order against the position by negating the position quantity.
        If price is null a market order, otherwise a limit order gets created.
        time_in_force must not be None when price is provided.
        """

        if price is None:
            order = Order.market(position.symbol, quantity=-position.quantity)
        elif price is not None and time_in_force is not None:
            order = Order.limit(
                position.symbol,
                quantity=-position.quantity,
                price=price,
                time_in_force=time_in_force,
            )
        else:
            raise ValueError(
                "Parameter 'time_in_force' must not be None if 'price' is not None"
            )

        return self.create_order(order)

    def cancel_orders(self, *orders: Order) -> List[Order]:
        return [
            self.client.futures_cancel_order(symbol=order.symbol, orderId=order.id)
            for order in orders
        ]

    def cancel_symbol_orders(self, symbol: str) -> List[Order]:
        canceled_orders: List[Dict] = self.client.futures_cancel_all_open_orders(
            symbol=symbol
        )

        return [Order.from_binance(order) for order in canceled_orders]

    def get_open_orders(self, symbol: str = None) -> List[Order]:
        open_orders: List[Dict] = self.client.futures_get_open_orders(symbol=symbol)
        return [Order.from_binance(order) for order in open_orders]

    def get_balances(self) -> List[Balance]:
        balances: List[Dict] = self.client.futures_account_balance()

        return [
            Balance(
                asset=balance["asset"],
                balance=balance["balance"],
                free=balance["withdrawAvailable"],
            )
            for balance in balances
            if float(balance["balance"]) > 0.0
        ]

    def get_positions(self) -> List[Position]:
        positions: List[Dict] = self.client.futures_account()["positions"]

        return [
            Position(**position)
            for position in positions
            if float(position["unrealizedProfit"]) > 0.0
        ]

    def get_position(self, symbol: str) -> Optional[Position]:
        positions: List[Dict] = self.client.futures_account()["positions"]

        for position in positions:
            if (
                symbol.upper() == position["symbol"]
                and float(position["unrealizedProfit"]) > 0.0
            ):
                return Position(**position)

    def get_all_symbol_info(self) -> List[SymbolInfo]:
        exchange_info: dict = self.client.futures_exchange_info()

        return [SymbolInfo(**symbol_info) for symbol_info in exchange_info["symbols"]]

    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        exchange_info: dict = self.client.futures_exchange_info()

        symbol = symbol.upper()
        for symbol_info in exchange_info["symbols"]:
            if symbol_info["symbol"] == symbol:
                return SymbolInfo(**symbol_info)

        raise ValueError(f"Invalid symbol: {symbol}")

    def set_leverage(self, symbol: str, leverage: int):
        self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
