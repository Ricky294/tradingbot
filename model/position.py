from typing import Union

from model import Order, TimeInForce


class Position:

    __slots__ = (
        "symbol",
        "side",
        "quantity",
        "entry_price",
        "leverage",
        # "initial_margin",
        # "maintenance_margin",
        # "unrealized_profit",
        # "position_initial_margin",
        # "open_order_initial_margin",
        # "isolated",
        # "max_notional",
        # "notional",
        # "isolated_wallet",
        # "update_time",
    )

    def __init__(
        self,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float,
        leverage: int,
        # initial_margin: float,
        # maintenance_margin: float,
        # unrealized_profit: float,
        # position_initial_margin: float,
        # open_order_initial_margin: float,
        # isolated: str,
        # max_notional: float,
        # notional: float,
        # isolated_wallet,
        # update_time: int,
    ):
        self.symbol = symbol
        self.side = side
        self.quantity = float(quantity)
        self.entry_price = float(entry_price)
        self.leverage = int(leverage)
        # self.initial_margin = float(initial_margin)
        # self.maintenance_margin = float(maintenance_margin)
        # self.unrealized_profit = float(unrealized_profit)
        # self.position_initial_margin = float(position_initial_margin)
        # self.open_order_initial_margin = float(open_order_initial_margin)
        # self.isolated = isolated
        # self.max_notional = float(max_notional)
        # self.notional = float(notional)
        # self.isolated_wallet = float(isolated_wallet)
        # self.update_time = int(update_time / 1000)

    @classmethod
    def from_binance(cls, data: dict):
        return cls(
            symbol=data["symbol"],
            side=data["positionSide"],
            quantity=data["positionAmt"],
            entry_price=data["entryPrice"],
            leverage=data["leverage"],
            # initial_margin=data["initialMargin"],
            # maintenance_margin=data["maintMargin"],
            # unrealized_profit=data["unrealizedProfit"],
            # position_initial_margin=data["positionInitialMargin"],
            # open_order_initial_margin=data["openOrderInitialMargin"],
            # isolated=data["isolated"],
            # max_notional=data["maxNotional"],
            # notional=data["notional"],
            # isolated_wallet=data["isolatedWallet"],
            # update_time=data["updateTime"] / 1000,
        )

    def reduce_position_market_order(self, quantity: float) -> Order:
        quantity = abs(quantity)
        if self.quantity > 0:
            quantity = -quantity

        return Order.market(symbol=self.symbol, quantity=quantity)

    def close_position_market_order(self) -> Order:
        return Order.market(symbol=self.symbol, quantity=-self.quantity)

    def close_position_limit_order(
        self,
        price: float,
        time_in_force: Union[str, TimeInForce] = "GTC",
    ) -> Order:
        """
        Creates an order against the position by negating the position quantity.
        If price is null a market order, otherwise a limit order gets created.
        time_in_force must not be None when price is provided.
        """

        order = Order.limit(
            symbol=self.symbol,
            quantity=-self.quantity,
            price=price,
            time_in_force=time_in_force,
        )

        return order
