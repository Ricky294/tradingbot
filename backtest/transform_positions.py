from typing import List

import numpy as np

from backtest.position import BacktestPosition

ENTRY_TIME_INDEX = 0
ENTRY_PRICE_INDEX = 1
ENTRY_QUANTITY_INDEX = 2

EXIT_TIME_INDEX = 3
EXIT_PRICE_INDEX = 4
EXIT_QUANTITY_INDEX = 5

PROFIT_INDEX = 6
SIDE_INDEX = 7
LEVERAGE_INDEX = 8


def middle_position_to_array(positions: List[BacktestPosition]):
    return np.array([
        tuple(position.times[1:-1] for position in positions),
        tuple(position.prices[1:-1] for position in positions),
        tuple(position.quantities[1:-1] for position in positions),
    ])


def positions_to_array(positions: List[BacktestPosition]):

    return np.array([
        tuple(position.times[0] for position in positions),
        tuple(position.prices[0] for position in positions),
        tuple(position.quantities[0] for position in positions),

        tuple(position.times[-1] for position in positions),
        tuple(position.prices[-1] for position in positions),
        tuple(position.quantities[-1] for position in positions),

        tuple(position.calculate_profit(position.prices[-1]) for position in positions),
        tuple(position.side for position in positions),
        tuple(position.leverage for position in positions),
    ])
