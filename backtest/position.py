from consts.trade_actions import LONG, SHORT
from model import Balance


class BacktestPosition:

    __slots__ = (
        "times", "prices", "quantities", "leverage"
    )

    def __init__(
            self,
            entry_time: int,
            entry_price: float,
            entry_quantity: float,
            leverage: int,
    ):
        if entry_quantity == 0:
            raise ValueError("Quantity must not be 0!")

        self.times = [entry_time]
        self.prices = [entry_price]
        self.quantities = [entry_quantity]
        self.leverage = leverage

    @property
    def side(self):
        return LONG if self.quantities[0] > 0 else SHORT

    def adjust(self, time: int, price: float, quantity: float):
        if self.is_closed():
            raise ValueError("Position is already closed!")

        self.times.append(time)
        self.prices.append(price)

        sum_quantity = sum(self.quantities) + quantity
        if (
            (self.side == LONG and sum_quantity < 0)
            or (self.side == SHORT and sum_quantity > 0)
        ):
            self.quantities.append(quantity - sum_quantity)
        else:
            self.quantities.append(quantity)

    def close(self, time: int, price: float):
        if self.is_closed():
            raise ValueError("Position is already closed!")

        self.times.append(time)
        self.prices.append(price)
        self.quantities.append(-sum(self.quantities))

    def calculate_profit(self, profit_price: float):
        costs = tuple(price * quantity for price, quantity in zip(self.prices, self.quantities))
        profits = tuple(profit_price * quantity - cost for cost, quantity in zip(costs, self.quantities))
        sum_profit = sum(profits) * self.leverage

        return sum_profit

    def is_closed(self):
        return sum(self.quantities) == 0

    def is_liquidated(self, balance: Balance, current_price: float):
        """
        current_price: Current low or high price.
        """
        profit = self.calculate_profit(current_price)

        return profit < 0 and abs(profit) >= balance.total
