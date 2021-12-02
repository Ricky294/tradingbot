from typing import Dict, List, Optional, Union

from binance.client import Client

from model import Order, TimeInForce, Balance, Position, SymbolInfo


def create_futures_batch_orders(client: Client, *orders: Order) -> List[Order]:
    """
    Creates multiple order at the same time (all fails or all gets created)
    Limitations: Binance can only create max. 5 orders in a batch
    """

    orders = {"batchOrders": [order.to_binance_order() for order in orders]}
    binance_orders = client.futures_place_batch_order(**orders)

    return [Order.from_binance(order) for order in binance_orders]


def create_futures_order(client: Client, order: Order) -> Order:
    order = client.futures_create_order(**order.to_binance_order())
    return Order.from_binance(order)


def create_futures_position_closing_order(
    client: Client,
    position: Position,
    price: float = None,
    time_in_force: Union[str, TimeInForce] = "GTC",
):
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

    return create_futures_order(client, order)


def cancel_futures_orders(client: Client, *orders: Order):
    return [
        client.futures_cancel_order(symbol=order.symbol, orderId=order.id)
        for order in orders
    ]


def cancel_futures_symbol_orders(client: Client, symbol: str) -> List[Order]:
    canceled_orders: List[Dict] = client.futures_cancel_all_open_orders(symbol=symbol)

    return [Order.from_binance(order) for order in canceled_orders]


def get_futures_open_orders(client: Client, symbol: str = None) -> List[Order]:
    open_orders: List[Dict] = client.futures_get_open_orders(symbol=symbol)
    return [Order.from_binance(order) for order in open_orders]


def get_futures_balances(client: Client) -> List[Balance]:
    balances: List[Dict] = client.futures_account_balance()

    return [
        Balance(
            asset=balance["asset"],
            balance=balance["balance"],
            free=balance["withdrawAvailable"],
        )
        for balance in balances
        if float(balance["balance"]) > 0.0
    ]


def get_futures_positions(client: Client) -> List[Position]:
    positions: List[Dict] = client.futures_account()["positions"]

    return [
        Position(**position)
        for position in positions
        if float(position["unrealizedProfit"]) > 0.0
    ]


def get_futures_position(client: Client, symbol: str) -> Optional[Position]:
    positions: List[Dict] = client.futures_account()["positions"]

    for position in positions:
        if (
            symbol.upper() == position["symbol"]
            and float(position["unrealizedProfit"]) > 0.0
        ):
            return Position(**position)


def get_all_futures_symbol_info(client: Client) -> List[SymbolInfo]:
    exchange_info: dict = client.futures_exchange_info()

    return [SymbolInfo(**symbol_info) for symbol_info in exchange_info["symbols"]]


def get_futures_symbol_info(client: Client, symbol: str) -> SymbolInfo:
    exchange_info: dict = client.futures_exchange_info()

    symbol = symbol.upper()
    for symbol_info in exchange_info["symbols"]:
        if symbol_info["symbol"] == symbol:
            return SymbolInfo(**symbol_info)

    raise ValueError(f"Invalid symbol: {symbol}")


def set_futures_leverage(client: Client, symbol: str, leverage: int):
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
