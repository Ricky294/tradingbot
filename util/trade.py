from typing import Union

import numpy as np
import talib

from consts.trade_actions import BUY, SELL
from model import Position
from model.balance import Balance
from model.order import OrderSide, OrderError, Order
import numba


@numba.jit(nopython=True)
def calculate_ha_open(open, close, ha_close):
    ha_open = np.empty(np.shape(open))
    ha_open[0] = (open[0] + close[0]) / 2

    for i in range(1, np.shape(open)[0]):
        ha_open[i] = (ha_open[i-1] + ha_close[i-1]) / 2

    return ha_open


def to_heikin_ashi(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
    ha_close = (open + high + low + close) / 4
    ha_open = calculate_ha_open(open, close, ha_close)
    ha_high = np.maximum.reduce((high, ha_open, ha_close))
    ha_low = np.minimum.reduce((low, ha_open, ha_close))

    return ha_open, ha_high, ha_low, ha_close


def talib_ma(type: str, period: int, data: np.ndarray) -> np.ndarray:
    return getattr(talib, type)(data, timeperiod=period)


def side_based_on_quantity(quantity: Union[float, int]):
    return BUY if quantity > 0 else SELL


def calculate_quantity(
    side: int, balance: Balance, price: float, percentage: float, leverage: int = 1
):
    quantity = balance.available / price * percentage * leverage
    return quantity if side == BUY else -quantity


def calculate_profit(order: Order, position: Position, leverage: int):
    return abs(position.entry_price - order.stop_price) * position.quantity * leverage


def calculate_pnl(
    entry_price: float,
    exit_price: float,
    quantity: float,
    side: Union[OrderSide, int],
    leverage: int = 1,
):
    """
    :return: Tuple of 3: (initial margin, pnl, roe)
    """

    side = str(side).upper()

    if side == BUY:
        pnl = (exit_price - entry_price) * quantity
    elif side == SELL:
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

    if side == BUY:
        return entry_price + diff
    elif side == SELL:
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
