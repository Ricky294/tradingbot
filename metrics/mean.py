from .metric import Metric


class Mean(Metric):
    def __init__(self, value=None, step=None):
        super(Mean, self).__init__(value, step)

    def call(self, value):
        result = (self.value * (self.steps - 1) + value) / self.steps
        self._value = result
