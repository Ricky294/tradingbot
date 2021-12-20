from abc import ABC


class Metric(ABC):
    def __init__(self, value=None, step=None):
        if value is None:
            value = 0
        if step is None:
            step = 0
        self._value = value
        self._steps = step

    def __call__(self, *args, **kwargs):
        self._steps += 1
        self.call(*args, **kwargs)

    def call(self, *args, **kwargs):
        raise NotImplementedError

    def result(self):
        return float(self._value)

    def reset(self):
        self._steps = 0
        self._value = 0

    @property
    def steps(self):
        return self._steps

    @property
    def value(self):
        return self._value
