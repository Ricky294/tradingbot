from typing import Union

from model.balance import Balance
from model.order import OrderSide, OrderError


def calculate_quantity(
    balance: Balance, price: float, percentage: float, leverage: int = 1
):
    # Be cautious! It's only works if you do not have ANY open orders/positions in place.
    # If you have open orders/position you need a more complex calculation considering other factors as well.
    return balance.free / price * percentage * leverage


def calculate_pnl(
    entry_price: float,
    exit_price: float,
    quantity: float,
    side: Union[OrderSide, str],
    leverage: int = 1,
):
    """
    :return: Tuple of 3: (initial margin, pnl, roe)
    """

    side = str(side).upper()

    if side == "BUY":
        pnl = (exit_price - entry_price) * quantity
    elif side == "SELL":
        pnl = (entry_price - exit_price) * quantity
    else:
        raise OrderError.side()

    initial_margin = quantity * entry_price / leverage
    roe = pnl / initial_margin

    return initial_margin, pnl, roe


def calculate_target_price(
    entry_price: float, roe: float, side: Union[OrderSide, str], leverage: int
):
    diff = entry_price * roe / leverage

    side = str(side).upper()

    if side == "BUY":
        return entry_price + diff
    elif side == "SELL":
        return entry_price - diff


# (max) position, maintenance margin, maintenance amount
maint_lookup_table = [
    (50_000, 0.4, 0),
    (250_000, 0.5, 50),
    (1_000_000, 1.0, 1_300),
    (10_000_000, 2.5, 16_300),
    (20_000_000, 5.0, 266_300),
    (50_000_000, 10.0, 1_266_300),
    (100_000_000, 12.5, 2_516_300),
    (200_000_000, 15.0, 5_016_300),
    (300_000_000, 25.0, 25_016_300),
    (500_000_000, 50.0, 100_016_300),
]


def binance_btc_liq_balance(wallet_balance, contract_qty, entry_price):
    for max_position, maint_margin_rate_pct, maint_amount in maint_lookup_table:
        maint_margin_rate = maint_margin_rate_pct / 100
        liq_price = (wallet_balance + maint_amount - contract_qty * entry_price) / (
            abs(contract_qty) * (maint_margin_rate - (1 if contract_qty >= 0 else -1))
        )
        base_balance = liq_price * abs(contract_qty)
        if base_balance <= max_position:
            break
    return liq_price


def calculate_liquidation_price(
    entry_price: float, quantity: float, balance: float, leverage: int
):
    min_balance = entry_price * quantity / leverage
    if min_balance > balance:
        raise OrderError("")
    return binance_btc_liq_balance(balance, quantity, entry_price)


print(calculate_liquidation_price(60_000, 0.003, 179, 2))
