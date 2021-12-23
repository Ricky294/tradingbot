import numpy as np
import pandas as pd

from consts.actions import BUY, SELL
from .basic import (
    all_time_low,
    all_time_high,
    return_on_investment,
    win_loss_ratio,
    biggest_winner,
    biggest_looser,
)


class Summary:

    def __init__(self, precision=3):
        self.precision = precision

    def print_price_summary(
            self,
            open_time: np.ndarray,
            open_price: np.ndarray,
            high_price: np.ndarray,
            low_price: np.ndarray,
    ):
        lowest_price_time, lowest_price = all_time_low(open_time, low_price)
        highest_price_time, highest_price = all_time_high(open_time, high_price)

        print(
            f"----------Price summary----------",
            f"All time low: {pd.to_datetime(lowest_price_time, unit='s')}, price: {lowest_price}",
            f"All time high: {pd.to_datetime(highest_price_time, unit='s')}, price: {highest_price}",
            f"---------------------------------",
            sep="\n",
        )

    def print_trade_summary(
            self,
            start_cash: float,
            side: np.ndarray,
            profit: np.ndarray,
            capital: np.ndarray,
    ):
        wins, losses, win_loss_rate = win_loss_ratio(profit)
        biggest_loss = biggest_looser(profit)
        biggest_win = biggest_winner(profit)

        total_profit, profit_ratio = return_on_investment(start_cash=start_cash, capital=capital)

        print(
            f"----------Trade results----------",
            f"Positions: {wins + losses}, Long: {len(side[side == BUY])}, Short: {len(side[side == SELL])}",
            f"Wins: {wins}, Losses: {losses}, Win/loss: {win_loss_rate:.{self.precision}f}",
            f"Biggest win: {biggest_win:.{self.precision}f}, Biggest loss: {biggest_loss:.{self.precision}f}",
            f"Total profit: {total_profit:.{self.precision}f}, Profit ratio: {profit_ratio:.{self.precision}f}",
            f"---------------------------------",
            sep="\n",
        )


