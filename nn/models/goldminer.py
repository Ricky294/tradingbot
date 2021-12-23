import torch as pt
import pickle
from torch.nn import Module, Linear, Dropout, TransformerEncoder, TransformerEncoderLayer, Conv1d, ModuleList
from torch.nn import functional as F
from hashlib import sha256
from encoding.time import TimeEncoder
from nn.layers import Time2Vec


class GoldMiner(Module):
    def __init__(
            self,
            d_input: int,
            seq_len: int,
            d_hidden: int,
            n_layers: int,
            device: str,
            dropout: float = 0.25
    ):
        super(GoldMiner, self).__init__()
        self.__d_input = d_input
        self.__seq_len = seq_len
        self.__d_hidden = d_hidden
        self.__d_feat_space = 256
        self.__n_layers = n_layers
        self.__device = device
        self.__time_encoding = pt.tensor(
            TimeEncoder()(self.__seq_len, self.__d_input, 0.01).T,
            device=self.__device
        )
        self.time_embedding = Time2Vec(
            self.__seq_len,
            self.__d_hidden,
            bias=True,
            device=device,
            dtype=pt.float32
        )
        self.conv_layer = Conv1d(
            self.__d_input,
            self.__d_feat_space,
            kernel_size=(3,),
            device=self.__device,
            dtype=pt.float32
        )
        self.feat_input_layer = Linear(
            self.__seq_len - 2,
            self.__d_feat_space,
            bias=True,
            device=self.__device,
            dtype=pt.float32
        )
        self.feat_layers = ModuleList(
            Linear(
                self.__d_feat_space,
                self.__d_feat_space,
                bias=True,
                device=self.__device,
                dtype=pt.float32
            )
            for _ in range(self.__n_layers)
        )
        self.time_embed_dropout = Dropout(dropout, inplace=True)
        self.feat_input_dropout = Dropout(dropout, inplace=True)
        self.feat_dropout = Dropout(dropout, inplace=True)
        self.conv_dropout = Dropout(dropout, inplace=True)
        self.reducer = Linear(self.__d_feat_space, 1, bias=True, device=self.__device, dtype=pt.float32)
        self.clz_layer = Linear(self.__d_feat_space, 3, bias=True, device=self.__device, dtype=pt.float32)

    def forward(self, series):
        x = series.to(self.__device)
        x += self.__time_encoding
        x = pt.transpose(x, -1, -2)
        x = self.conv_layer(x)
        x = F.gelu(x)
        x = self.conv_dropout(x)
        x = self.feat_input_layer(x)
        x = self.feat_input_dropout(x)
        for layer in self.feat_layers:
            x = layer(x)
            x = F.gelu(x)
            x = self.feat_dropout(x)
        x = self.reducer(x)
        x = pt.squeeze(x, dim=-1)
        out = self.clz_layer(x)
        return out

    @property
    def config(self):
        return {
            "name": self.__class__.__name__,
            "d_input": self.__d_input,
            "seq_len": self.__seq_len,
            "d_hidden": self.__d_hidden,
            "n_layers": self.__n_layers,
            "device": self.__device
        }

    def __str__(self):
        return sha256(
            pickle.dumps(self.config) +
            GoldMiner.forward.__code__.co_code
        ).hexdigest()
