from enum import Enum
from typing import Union, Dict

from consts import actions
from consts.actions import BUY, SELL
from consts.order import (
    MARKET_ORDER, LIMIT_ORDER,
    TAKE_PROFIT_MARKET_ORDER, STOP_LOSS_MARKET_ORDER,
    TAKE_PROFIT_LIMIT_ORDER, STOP_LOSS_LIMIT_ORDER,
)
from model.symbol_info import SymbolInfo
from util.common import remove_none, generate_ascii, generate_random_string


def generate_client_order_id() -> str:
    max_char = 36

    zero_to_nine = "".join(generate_ascii(48, 58))
    a_to_z = "".join(generate_ascii(65, 91))
    A_to_Z = "".join(generate_ascii(97, 123))

    return generate_random_string(r".:/_-" + zero_to_nine + a_to_z + A_to_Z, max_char)


class OrderSide(Enum):
    BUY = actions.BUY
    SELL = actions.SELL

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


class Side(Enum):
    SELL = actions.SELL
    BUY = actions.BUY

    @staticmethod
    def from_quantity(quantity):
        if quantity > 0:
            return Side.BUY
        else:
            return Side.SELL

    def __str__(self):
        return self.value


# Docs: https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
class Order:

    __slots__ = (
        "id",
        "symbol",
        "type",
        "status",
    )

    def __init__(
            self,
            symbol: str,
            type: Union[OrderType, str],
            id: int = None,
            status: str = None,
    ):
        self.symbol = symbol
        self.type = str(type).upper()
        self.id = id
        self.status = status

    def __eq__(self, other):
        if other is Order:
            return self.id == other.id
        return False

    @staticmethod
    def from_binance(data: dict) -> 'Order':
        order_type = data["type"]
        if order_type == MARKET_ORDER:
            return MarketOrder(
                id=data["orderId"],
                symbol=data["symbol"],
                status=data["status"],
                quantity=float(data["origQty"]),
            )
        if order_type == LIMIT_ORDER:
            return LimitOrder(
                id=data["orderId"],
                symbol=data["symbol"],
                status=data["status"],
                price=float(data["price"]),
                time_in_force=data["timeInForce"],
                quantity=float(data["origQty"]),
            )

    @property
    def side(self):
        if hasattr(self, "quantity"):
            if self.quantity > 0:
                return BUY
            else:
                return SELL
        if hasattr(self, "close_side"):
            return str(self.close_side)

    @staticmethod
    def market(
        symbol: str,
        quantity: float,
    ):
        return MarketOrder(
            symbol=symbol,
            quantity=quantity,
        )

    @staticmethod
    def limit(
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: Union[TimeInForce, str] = "GTC",
    ):
        return LimitOrder(
            symbol=symbol,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
        )

    @staticmethod
    def stop_limit(
        symbol: str,
        price: float,
        stop_price: float,
    ):
        return StopLossLimitOrder(
            symbol=symbol,
            price=price,
            stop_price=stop_price,
        )

    @staticmethod
    def take_profit_limit(
        symbol: str,
        price: float,
        stop_price: float,
    ):
        return TakeProfitLimitOrder(
            symbol=symbol,
            price=price,
            stop_price=stop_price,
        )

    @staticmethod
    def stop_market(
        symbol: str,
        stop_price: float,
    ):
        return StopLossMarketOrder(
            symbol=symbol,
            stop_price=stop_price,
        )

    @staticmethod
    def take_profit_market(
        symbol: str,
        stop_price: float,
    ):
        return TakeProfitMarketOrder(
            symbol=symbol,
            stop_price=stop_price,
        )

    def to_binance_order(self):
        dct = {
            "symbol": str(self.symbol),
            "type": str(self.type),
        }

        if hasattr(self, "time_in_force"):
            dct["timeInForce"] = str(self.time_in_force)
        if hasattr(self, "side"):
            dct["side"] = str(self.side).upper()
        if hasattr(self, "price"):
            dct["price"] = str(self.price)
        if hasattr(self, "stop_price"):
            dct["stopPrice"] = str(self.stop_price)

        if hasattr(self, "quantity"):
            if isinstance(self.quantity, Side):
                dct["closePosition"] = "true"
            else:
                dct["quantity"] = str(abs(self.quantity))

        return remove_none(dct)


class MarketOrder(Order):

    def __init__(
            self,
            symbol: Union[SymbolInfo, str],
            quantity: float,
            status=None,
            id=None,
    ):
        super().__init__(
            symbol=symbol,
            type=MARKET_ORDER,
            status=status,
            id=id,
        )
        self.quantity = quantity


class LimitOrder(Order):

    __slots__ = "quantity", "price", "time_in_force"

    def __init__(
            self,
            symbol: Union[SymbolInfo, str],
            quantity: float,
            price: float,
            time_in_force: Union[str, TimeInForce] = "GTC",
            status=None,
            id=None,
    ):
        super().__init__(
            symbol=symbol,
            type=LIMIT_ORDER,
            status=status,
            id=id,
        )
        self.quantity = quantity
        self.price = price
        self.time_in_force = time_in_force


class TakeProfitMarketOrder(Order):

    __slots__ = "stop_price"

    def __init__(
            self,
            symbol: Union[SymbolInfo, str],
            stop_price: float,
            status=None,
            id=None,
    ):
        super().__init__(
            symbol=symbol,
            type=TAKE_PROFIT_MARKET_ORDER,
            status=status,
            id=id,
        )
        self.stop_price = stop_price


class TakeProfitLimitOrder(Order):

    __slots__ = "stop_price", "price"

    def __init__(
            self,
            symbol: Union[SymbolInfo, str],
            price: float,
            stop_price: float,
            status=None,
            id=None,
    ):
        super().__init__(
            symbol=symbol,
            type=TAKE_PROFIT_LIMIT_ORDER,
            status=status,
            id=id,
        )
        self.stop_price = stop_price
        self.price = price


class StopLossMarketOrder(Order):

    __slots__ = "stop_price"

    def __init__(
            self,
            symbol: Union[SymbolInfo, str],
            stop_price: float,
            status=None,
            id=None,
    ):
        super().__init__(
            symbol=symbol,
            type=STOP_LOSS_MARKET_ORDER,
            status=status,
            id=id,
        )
        self.stop_price = stop_price


class StopLossLimitOrder(Order):

    __slots__ = "stop_price", "price"

    def __init__(
            self,
            symbol: Union[SymbolInfo, str],
            price: float,
            stop_price: float,
            status=None,
            id=None,
    ):
        super().__init__(
            symbol=symbol,
            type=STOP_LOSS_LIMIT_ORDER,
            status=status,
            id=id,
        )
        self.stop_price = stop_price
        self.price = price


def __stop_loss_take_profit_order(
    symbol: str, quantity: float, stop_price: float = None, profit_price: float = None
):
    close_position_side = Side.SELL if quantity > 0 else Side.BUY

    orders = {}
    if stop_price is not None:
        stop_order = Order.stop_market(
            symbol=symbol,
            stop_price=stop_price,
        )
        orders["stop_order"] = stop_order

    if profit_price is not None:
        profit_order = Order.take_profit_market(
            symbol=symbol,
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
