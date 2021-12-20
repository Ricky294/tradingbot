import pickle

from hashlib import sha256

import torch as pt
from torch.nn.modules import Module, Linear, GELU, ModuleList, Dropout


class Miner(Module):

    def __init__(
            self,
            d_input: int,
            d_hidden: int,
            n_layers: int,
            device: str,
            dropout: float = 0.25,
    ):
        super(Miner, self).__init__()
        self.__d_input = d_input
        self.__d_hidden = d_hidden
        self.__n_layers = n_layers
        self.__device = device
        self.input_layer = Linear(
            in_features=self.__d_input,
            out_features=self.__d_hidden,
            bias=True,
            device=self.__device,
            dtype=pt.float32,
        )
        self.hidden_layers = ModuleList(
            modules=[
                Linear(
                    in_features=self.__d_hidden,
                    out_features=self.__d_hidden,
                    bias=True,
                    device=self.__device,
                    dtype=pt.float32,
                )
                for _ in range(self.__n_layers)
            ]
        )
        self.dropout = Dropout(dropout)
        self.gelu = GELU()
        self.clz_layer = Linear(
            in_features=self.__d_hidden,
            out_features=3,
            bias=True,
            device=self.__device,
            dtype=pt.float32,
        )

    @property
    def config(self):
        return {
            "name": self.__class__.__name__,
            "d_input": self.__d_input,
            "d_hidden": self.__d_hidden,
            "n_layers": self.__n_layers,
            "device": self.__device,
        }

    def __str__(self):
        return sha256(
            pickle.dumps({
                **self.config,
                "forward": Miner.forward.__code__.co_code,
            })
        ).hexdigest()

    def forward(self, close_series, training=True):
        self.input_layer.training = training
        self.dropout.training = training
        for hl in self.hidden_layers:
            hl.training = training

        self.clz_layer.training = training

        x = pt.tensor(close_series, device=self.__device, dtype=pt.float32)
        x = self.input_layer(x)
        x = self.dropout(x)
        for hl in self.hidden_layers:
            x = hl(x)
            x = self.gelu(x)
            x = self.dropout(x)

        x = self.clz_layer(x)
        return x
