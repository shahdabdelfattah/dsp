import numpy as np

class DiscreteSignal:
    def __init__(self, indices, values):
        if len(indices) == 0 or len(values) == 0:
            raise ValueError("indices and values cannot be empty")
        if len(indices) != len(values):
            raise ValueError(f"got {len(indices)} indices but {len(values)} values")

        self._indices = np.array(indices)
        self._values = np.array(values)

    @property
    def indices(self):
        return self._indices

    @property
    def values(self):
        return self._values