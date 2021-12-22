import torch as pt
from torch.nn import Module, Linear


class Time2Vec(Module):
    def __init__(
            self,
            d_input: int,
            d_output: int,
            bias=True,
            device: str = None,
            dtype=None
    ):
        assert d_output > 1, 'Output dimension should be greater than 1.'
        super(Time2Vec, self).__init__()
        self.__d_input = d_input
        self.__d_output = d_output
        self.non_periodic_feats = Linear(
            self.__d_input,
            1,
            bias=bias,
            device=device,
            dtype=dtype
        )
        self.periodic_feats = Linear(
            self.__d_input,
            self.__d_output - 1,
            bias=bias,
            device=device,
            dtype=dtype
        )
        self.activation = pt.sin

    def time2vec(self, tau):
        non_periodic_feats = self.non_periodic_feats(tau)
        periodic_feats = self.periodic_feats(tau)
        periodic_feats = self.activation(periodic_feats)
        return pt.concat([non_periodic_feats, periodic_feats], dim=-1)

    def forward(self, tau):
        return self.time2vec(tau)
