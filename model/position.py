from model import Order, OrderType


class Position:
    def __init__(self, **kwargs):
        self.symbol = kwargs["symbol"]
        self.initial_margin = float(kwargs["initialMargin"])
        self.maintenance_margin = float(kwargs["maintMargin"])
        self.unrealized_profit = float(kwargs["unrealizedProfit"])
        self.position_initial_margin = float(kwargs["positionInitialMargin"])
        self.open_order_initial_margin = float(kwargs["openOrderInitialMargin"])
        self.leverage = int(kwargs["leverage"])
        self.isolated = kwargs["isolated"]
        self.entry_price = float(kwargs["entryPrice"])
        self.max_notional = float(kwargs["maxNotional"])
        self.side = kwargs["positionSide"]
        self.quantity = float(kwargs["positionAmt"])
        self.notional = float(kwargs["notional"])
        self.isolated_wallet = float(kwargs["isolatedWallet"])
        self.update_time = int(kwargs["updateTime"] / 1000)

    def reduce_position(self, quantity: float) -> Order:
        quantity = abs(quantity)
        if self.quantity > 0:
            quantity = -quantity

        return Order(symbol=self.symbol, type=OrderType.MARKET, quantity=quantity)

    def close_position(self) -> Order:
        return Order(symbol=self.symbol, type=OrderType.MARKET, quantity=-self.quantity)
