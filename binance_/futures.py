from typing import Dict, List, Optional, Callable

from binance.client import Client

from model.order import Order
from model.balance import Balance
from model.position import Position
from model.symbol_info import SymbolInfo


def inject_trade_info(
    client: Client,
    callback: Callable[
        [List[Position], List[Order], List[Balance], List[SymbolInfo]], any
    ],
    symbol: str = None,
):
    balances = get_futures_balances(client)
    positions: List[Position]
    orders: List[Order]
    symbol_info: List[SymbolInfo]

    if symbol is not None:
        optional_position = get_futures_position(client, symbol=symbol)

        positions = []
        if optional_position is not None:
            positions = [optional_position]

        orders = get_futures_open_orders(client, symbol=symbol)
        symbol_info = [get_futures_symbol_info(client, symbol=symbol)]
    else:
        positions = get_futures_positions(client)
        orders = get_futures_open_orders(client)
        symbol_info = get_futures_info(client)

    return callback(positions, orders, balances, symbol_info)


def create_futures_order(client: Client, order: Order) -> Order:
    order = client.futures_create_order(**order.to_binance_order())
    return Order.from_binance(order)


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


def get_futures_info(client: Client) -> List[SymbolInfo]:
    exchange_info: dict = client.futures_exchange_info()

    return [SymbolInfo(**symbol_info) for symbol_info in exchange_info["symbols"]]


def get_futures_symbol_info(client: Client, symbol: str) -> SymbolInfo:
    exchange_info: dict = client.futures_exchange_info()

    for symbol_info in exchange_info["symbols"]:
        if symbol_info["symbol"] == symbol.upper():
            return SymbolInfo(**symbol_info)


def set_futures_leverage(client: Client, symbol: str, leverage: int):
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
