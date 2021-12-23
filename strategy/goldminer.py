import numpy as np
import torch as pt
from typing import Dict

from abstract import FuturesTrader
from consts.actions import LONG, SHORT, NONE
from consts.candle_column_index import CLOSE_PRICE_INDEX
from checkpointing.load import load_model
from model import SymbolTradeInfo, Balance, Order
from nn.models import GoldMiner
from strategy import Strategy
from util.trade import calculate_quantity
from matils import softmax
from matils.norm import normalize, normalize_around_price


class GoldMinerStrategy(Strategy):
    def __init__(
            self,
            symbol: str,
            trader: FuturesTrader,
    ):
        super().__init__(symbol, trader)
        d_input = 5
        seq_len = 512
        d_hidden = 1024
        n_layers = 4
        device = "cuda"
        self.model = GoldMiner(
            d_input=d_input,
            seq_len=seq_len,
            d_hidden=d_hidden,
            n_layers=n_layers,
            device=device,
        )
        load_model(self.model)
        self.model.training = False
        self.model.requires_grad_(False)
        self.signal = NONE

    def on_candle(
            self,
            candles: np.ndarray,
            trade_info: SymbolTradeInfo,
            balances: Dict[str, Balance],
    ):
        model_input = candles[-self.model.config["seq_len"]:, 1:].copy()
        model_input[:, :4] = normalize_around_price(model_input[:, :4], price=model_input[-1, 3])
        model_input[:, 4] = normalize(model_input[:, 4])
        model_input = model_input[None, :]
        model_input = pt.tensor(model_input, dtype=pt.float32, device=self.model.config["device"])

        logits = self.model(model_input)
        logits = logits.detach().to("cpu").numpy()[0]
        probs = softmax(logits)
        if probs[2] >= 0.8:
            signal = LONG
        elif probs[1] >= 0.8:
            signal = SHORT
        else:
            signal = NONE
        #signal = int(np.argmax(probs))

        if signal != NONE:
            if self.signal != signal:
                self.signal = signal
                if self.trader.get_position(trade_info.symbol) is not None:
                    self.trader.close_position()

            if self.trader.get_position(trade_info.symbol) is None:
                self.trader.cancel_orders(trade_info.symbol)

                latest_close = candles[-1][CLOSE_PRICE_INDEX]
                quantity = calculate_quantity(
                    side=signal,
                    balance=balances["USDT"],
                    leverage=self.trader.get_leverage(trade_info.symbol),
                    price=latest_close,
                    percentage=self.trader.trade_ratio,
                )

                stop_loss_price = (
                    latest_close - latest_close * 1 * self.trader.trade_ratio
                    if signal == LONG
                    else latest_close + latest_close * 1 * self.trader.trade_ratio
                )
                take_profit_price = (
                    latest_close - latest_close * self.trader.trade_ratio
                    if signal == SHORT
                    else latest_close + latest_close * self.trader.trade_ratio
                )

                self.trader.create_orders(
                    Order.market(
                        symbol=trade_info.symbol,
                        quantity=quantity,
                    ),
                    Order.take_profit_market(
                        symbol=trade_info.symbol,
                        quantity=-quantity,
                        stop_price=take_profit_price,
                    ),
                    Order.stop_market(
                        symbol=trade_info.symbol,
                        quantity=-quantity,
                        stop_price=stop_loss_price,
                    ),
                )
