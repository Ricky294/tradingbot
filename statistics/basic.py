import numpy as np


def all_time_high(dates: np.ndarray, high_prices: np.ndarray):
    max_index = np.argmax(high_prices)

    return dates[max_index], np.max(high_prices)


def all_time_low(dates: np.ndarray, low_prices: np.ndarray):
    min_index = np.argmin(low_prices)

    return dates[min_index], np.min(low_prices)


def biggest_winner(profit):
    return np.max(profit)


def biggest_looser(profit: np.ndarray):
    return np.min(profit)


def cash_ratio(start_cash: float, end_cash: float):
    return end_cash / start_cash


def win_ratio(wins: int, losses: int):

    return wins / (wins + losses)


def maximum_drawdown():
    pass


def drawdowns_greater_than():
    pass

