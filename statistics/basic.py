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


def return_on_investment(start_cash: float, capital: np.ndarray):
    """
    Returns: (total return, ratio)
    """
    last_capital = capital[-1]
    return last_capital - start_cash, last_capital / start_cash


def win_loss_ratio(profit: np.ndarray):
    wins = len(profit[profit > 0])
    losses = len(profit[profit < 0])
    return wins, losses, wins / losses


def maximum_drawdown():
    pass


def drawdowns_greater_than():
    pass


"""
n = 1000
xs = np.random.randn(n).cumsum()
i = np.argmax(np.maximum.accumulate(xs) - xs)   # end of the period
j = np.argmax(xs[:i])                           # start of period

plt.plot(xs)
plt.plot([i, j], [xs[i], xs[j]], 'o', color='Red', markersize=10)
plt.show()
"""
