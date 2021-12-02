from enum import Enum
from typing import Union, Dict

from model.symbol_info import SymbolInfo
from util import remove_none, round_down, generate_ascii, generate_random_string


def generate_client_order_id() -> str:
    max_char = 36

    zero_to_nine = "".join(generate_ascii(48, 58))
    a_to_z = "".join(generate_ascii(65, 91))
    A_to_Z = "".join(generate_ascii(97, 123))

    return generate_random_string(r".:/_-" + zero_to_nine + a_to_z + A_to_Z, max_char)


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

    @classmethod
    def side(cls):
        return cls(f"Valid values for side: {(side.value for side in OrderSide)}")

    @classmethod
    def time_in_force(cls):
        return cls(
            f"Valid values for time in force: {(tif.value for tif in TimeInForce)}"
        )

    @classmethod
    def type(cls):
        return cls(f"Valid values for order type: {(ot.value for ot in OrderType)}")

    @classmethod
    def add_reduce(cls):
        return cls(f"Valid values for order action {(oa.value for oa in OrderAction)}")


class ClosePosition(Enum):
    SELL = "SELL"
    BUY = "BUY"

    def __str__(self):
        return self.value


# Docs: https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
class Order:
    def __init__(
        self,
        symbol: Union[SymbolInfo, str],
        type: Union[OrderType, str],
        quantity: Union[float, int, ClosePosition],
        price: float = None,
        stop_price: float = None,
        time_in_force: Union[TimeInForce, str] = None,
        id: int = None,
        status: str = None,
    ):
        self.quantity = quantity
        if isinstance(symbol, SymbolInfo):
            self.symbol = symbol.symbol
            if isinstance(quantity, (float, int)):
                self.quantity = round_down(quantity, symbol.quantity_precision)
            self.price = round_down(price, symbol.price_precision)
            self.stop_price = round_down(stop_price, symbol.price_precision)
        else:
            self.symbol = symbol.upper()
            if isinstance(quantity, (float, int)):
                self.quantity = quantity
            self.price = price
            self.stop_price = stop_price

        if isinstance(quantity, ClosePosition):
            self.side = str(quantity)
        elif quantity > 0:
            self.side = "BUY"
        else:
            self.side = "SELL"

        self.type = str(type).upper()

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
            quantity=float(data["origQty"]),
            type=data["type"],
        )

    @classmethod
    def market(
        cls,
        symbol: str,
        quantity: float,
    ):
        return cls(
            symbol=symbol,
            type="MARKET",
            quantity=quantity,
        )

    @classmethod
    def limit(
        cls,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: Union[TimeInForce, str] = "GTC",
    ):
        return cls(
            symbol=symbol,
            type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
        )

    @classmethod
    def stop_limit(
        cls,
        symbol: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: Union[TimeInForce, str] = "GTC",
    ):
        return cls(
            symbol=symbol,
            type="STOP",
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
        )

    @classmethod
    def take_profit_limit(
        cls,
        symbol: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: Union[TimeInForce, str] = "GTC",
    ):
        return cls(
            symbol=symbol,
            type="TAKE_PROFIT",
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
        )

    @classmethod
    def stop_market(
        cls,
        symbol: str,
        quantity: Union[float, ClosePosition],
        stop_price: float,
    ):
        return cls(
            symbol=symbol,
            type="STOP_MARKET",
            quantity=quantity,
            stop_price=stop_price,
        )

    @classmethod
    def take_profit_market(
        cls,
        symbol: str,
        quantity: Union[float, ClosePosition],
        stop_price: float,
    ):
        return cls(
            symbol=symbol,
            type="TAKE_PROFIT_MARKET",
            quantity=quantity,
            stop_price=stop_price,
        )

    def to_binance_order(self):
        dct = {
            "symbol": str(self.symbol),
            "timeInForce": str(self.time_in_force),
            "side": str(self.side).upper(),
            "type": str(self.type),
            "price": str(self.price),
            "stopPrice": str(self.stop_price),
        }

        if isinstance(self.quantity, ClosePosition):
            dct["closePosition"] = "true"
        else:
            dct["quantity"] = str(abs(self.quantity))

        return remove_none(dct)


def __stop_loss_take_profit_order(
    symbol: str, quantity: float, stop_price: float = None, profit_price: float = None
):
    close_position_side = ClosePosition.SELL if quantity > 0 else ClosePosition.BUY

    orders = {}
    if stop_price is not None:
        stop_order = Order.stop_market(
            symbol=symbol,
            quantity=close_position_side,
            stop_price=stop_price,
        )
        orders["stop_order"] = stop_order

    if profit_price is not None:
        profit_order = Order.take_profit_market(
            symbol=symbol,
            quantity=close_position_side,
            stop_price=profit_price,
        )
        orders["profit_order"] = profit_order

    return orders


def market_order_with_stop_loss_take_profit(
    symbol: Union[str, SymbolInfo],
    quantity: float,
    stop_price: float = None,
    profit_price: float = None,
) -> Dict[str, Order]:

    order = Order.market(
        symbol=symbol,
        quantity=quantity,
    )

    orders = {
        "order": order,
        **__stop_loss_take_profit_order(
            symbol=symbol,
            quantity=quantity,
            stop_price=stop_price,
            profit_price=profit_price,
        ),
    }

    return orders


def limit_order_with_stop_loss_take_profit(
    symbol: Union[str, SymbolInfo],
    quantity: float,
    price: float,
    time_in_force: Union[str, TimeInForce] = "GTC",
    stop_price: float = None,
    profit_price: float = None,
) -> Dict[str, Order]:

    order = Order.limit(
        symbol=symbol,
        quantity=quantity,
        price=price,
        time_in_force=time_in_force,
    )

    orders = {
        "order": order,
        **__stop_loss_take_profit_order(
            symbol=symbol,
            quantity=quantity,
            stop_price=stop_price,
            profit_price=profit_price,
        ),
    }

    return orders
