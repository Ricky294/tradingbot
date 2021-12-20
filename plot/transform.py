from typing import Dict

import numpy as np

from util.numpy import map_match


def extend_data(
        open_time: np.ndarray,
        entry_time: np.ndarray,
        entry_price: np.ndarray,
        exit_time: np.ndarray,
        exit_price: np.ndarray,
        side: np.ndarray,
        quantity: np.ndarray,
        profit: np.ndarray,
        starting_capital: float,
) -> Dict[str, np.ndarray]:

    entry_time_extended = map_match(open_time, entry_time)
    exit_time_extended = map_match(open_time, exit_time)

    entry_price_extended = np.copy(entry_time_extended)
    entry_price_extended[entry_price_extended > 0.0] = entry_price

    quantity_extended = np.copy(entry_time_extended)
    quantity_extended[quantity_extended > 0.0] = quantity

    side_extended = np.copy(entry_time_extended)
    side_extended[side_extended > 0.0] = side

    exit_price_extended = np.copy(exit_time_extended)
    exit_price_extended[exit_price_extended > 0.0] = exit_price

    profit_extended = np.copy(exit_time_extended)
    profit_extended[profit_extended > 0.0] = profit

    capital_extended = np.cumsum(profit_extended) + starting_capital

    entry_time_extended[entry_time_extended == 0.0] = np.nan
    exit_time_extended[exit_time_extended == 0.0] = np.nan

    return {
        "entry_time": entry_time_extended,
        "entry_price": entry_price_extended,
        "exit_time": exit_time_extended,
        "exit_price": exit_price_extended,
        "profit": profit_extended,
        "capital": capital_extended,
        "side": side_extended,
        "quantity": quantity_extended,
    }
