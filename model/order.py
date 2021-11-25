from enum import Enum
from typing import Union

from util import remove_none


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self):
        return self.value


class TimeInForce(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTX = "GTX"

    def __str__(self):
        return self.value


class OrderAction(Enum):
    ADD = "ADD"
    REDUCE = "REDUCE"

    def __str__(self):
        return self.value


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP"
    STOP_MARKET = "STOP_MARKET"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"
    TRAILING_STOP_MARKET = "TRAILING_STOP_MARKET"

    def __str__(self):
        return self.value


class OrderError(Exception):
    def __init__(self, message):
        super().__init__(message)


# Docs: https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
class Order:
    def __init__(
        self,
        symbol: str,
        side: Union[OrderSide, str],
        type: Union[OrderType, str],
        reduce_or_add: Union[OrderAction, str],
        quantity: float,
        price: float = None,
        stop_price: float = None,
        time_in_force: Union[TimeInForce, str] = None,
        id: int = None,
        status: str = None,
    ):
        self.symbol = symbol.upper()
        self.side = str(side).upper()
        self.type = str(type).upper()
        self.quantity = quantity
        self.reduce_or_add = str(reduce_or_add).upper()
        self.price = price
        self.stop_price = stop_price

        self.time_in_force = None
        if time_in_force is not None:
            self.time_in_force = str(time_in_force).upper()

        self.id = id
        self.status = status

    @classmethod
    def from_binance(cls, data: dict):
        return cls(
            id=data["orderId"],
            symbol=data["symbol"],
            status=data["status"],
            price=float(data["price"]),
            stop_price=float(data["stopPrice"]),
            time_in_force=data["timeInForce"],
            side=data["side"],
            reduce_or_add="REDUCE" if data["reduceOnly"] else "ADD",
            quantity=float(data["origQty"]),
            type=data["type"],
        )

    @classmethod
    def market(
        cls,
        symbol: str,
        side: Union[OrderSide, str],
        reduce_or_add: Union[OrderAction, str],
        quantity: float,
    ):
        return cls(
            symbol=symbol,
            type="MARKET",
            side=side,
            quantity=quantity,
            reduce_or_add=reduce_or_add,
        )

    @classmethod
    def limit(
        cls,
        symbol: str,
        side: Union[OrderSide, str],
        reduce_or_add: Union[OrderAction, str],
        quantity: float,
        price: float,
        time_in_force: Union[TimeInForce, str] = "GTC",
    ):
        return cls(
            symbol=symbol,
            type="LIMIT",
            side=side,
            reduce_or_add=reduce_or_add,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
        )

    @classmethod
    def stop_limit(
        cls,
        symbol: str,
        side: Union[OrderSide, str],
        reduce_or_add: Union[OrderAction, str],
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: Union[TimeInForce, str] = "GTC",
    ):
        return cls(
            symbol=symbol,
            side=side,
            type="STOP",
            reduce_or_add=reduce_or_add,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
        )

    @classmethod
    def take_profit_limit(
        cls,
        symbol: str,
        side: Union[OrderSide, str],
        reduce_or_add: Union[OrderAction, str],
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: Union[TimeInForce, str] = "GTC",
    ):
        return cls(
            symbol=symbol,
            side=side,
            type="TAKE_PROFIT",
            reduce_or_add=reduce_or_add,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
        )

    @classmethod
    def stop_market(
        cls,
        symbol: str,
        side: Union[OrderSide, str],
        reduce_or_add: Union[OrderAction, str],
        quantity: float,
        stop_price: float,
    ):
        return cls(
            symbol=symbol,
            side=side,
            type="STOP_MARKET",
            reduce_or_add=reduce_or_add,
            quantity=quantity,
            stop_price=stop_price,
        )

    @classmethod
    def take_profit_market(
        cls,
        symbol: str,
        side: Union[OrderSide, str],
        reduce_or_add: Union[OrderAction, str],
        quantity: float,
        stop_price: float,
    ):
        return cls(
            symbol=symbol,
            side=side,
            type="TAKE_PROFIT_MARKET",
            reduce_or_add=reduce_or_add,
            quantity=quantity,
            stop_price=stop_price,
        )

    def to_binance_order(self):
        dct = {
            "symbol": self.symbol,
            "timeInForce": self.time_in_force,
            "reduceOnly": True if self.reduce_or_add == "REDUCE" else False,
            "side": self.side,
            "type": self.type,
            "quantity": self.quantity,
            "stopPrice": self.stop_price,
            "price": self.price,
        }

        return remove_none(dct)
