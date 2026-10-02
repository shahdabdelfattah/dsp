import numpy as np

class DiscreteSignal:
    def __init__(self, indices, values):
        self._indices = np.array(indices)
        self._values = np.array(values)

    @property
    def indices(self):
        return self._indices

    @property
    def values(self):
        return self._values