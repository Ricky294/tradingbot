import numpy as np
import torch as pt

from trader.core.interface import FuturesTrader
from trader.core.const.trade_actions import LONG, SHORT, NONE
from trader.core.const.candle_index import CLOSE_PRICE_INDEX
from checkpointing.load import load_model
from nn.models import GoldMiner
from strategy import Strategy
from matils import softmax
from matils.norm import normalize, normalize_around_price


class GoldMinerStrategy(Strategy):
    def __init__(
            self,
            symbol: str,
            trader: FuturesTrader,
            trade_ratio: float,
            asset: str,
            leverage: int,
    ):
        super().__init__(symbol=symbol, trader=trader, trade_ratio=trade_ratio, asset=asset, leverage=leverage)
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

    def __call__(
            self,
            candles: np.ndarray,
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
                if self.trader.get_position(self.symbol) is not None:
                    self.trader.close_position(self.symbol)

            if self.trader.get_position(self.symbol) is None:
                self.trader.cancel_orders(self.symbol)

                latest_close = candles[-1][CLOSE_PRICE_INDEX]
                quantity = self.get_quantity(
                    signal=signal,
                    price=latest_close,
                )

                stop_loss_price = (
                    latest_close - latest_close * 1 * self.trade_ratio
                    if signal == LONG
                    else latest_close + latest_close * 1 * self.trade_ratio
                )
                take_profit_price = (
                    latest_close - latest_close * self.trade_ratio
                    if signal == SHORT
                    else latest_close + latest_close * self.trade_ratio
                )

                self.enter_position(
                    quantity=quantity,
                    take_profit_price=take_profit_price,
                    stop_loss_price=stop_loss_price,
                )
