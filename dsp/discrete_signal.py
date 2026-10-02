import numpy as np

class DiscreteSignal:
    def __init__(self, indices, values, name = "s"):
        idx = np.array(indices, dtype=float)
        val = np.array(values, dtype=float)

        if len(idx) == 0 or len(val) == 0:
            raise ValueError("indices and values cannot be empty")
        
        if len(idx) != len(val):
            raise ValueError(f"got {len(idx)} indices but {len(val)} values")

        if not np.all(np.isfinite(idx)):
            raise ValueError("indices must be finite numbers")
        if not np.all(np.isfinite(val)):
            raise ValueError("values must be finite numbers")

        if not np.array_equal(idx, np.round(idx)):
            raise ValueError("indices must be whole numbers")

        idx = idx.astype(int)

        order = np.argsort(idx)
        idx = idx[order]
        val = val[order]

        diff = np.diff(idx)
        dups = idx[1:][diff == 0]
        if dups.size > 0:
            raise ValueError("duplicate sample indices found")

        idx.setflags(write=False)
        val.setflags(write=False)

        self._indices = idx
        self._values = val
        self.name = name

    def value_at(self, idx):
        if not np.isfinite(idx):
            raise ValueError("index must be finite")
        if not np.array_equal(idx, np.round(idx)):
            raise ValueError("index must be a whole number")
        idx = int(idx)

        if idx < self.start or idx > self.end:
            return 0.0

        pos = np.searchsorted(self._indices, idx)
        if pos < len(self._indices) and self._indices[pos] == idx:
            return float(self._values[pos])
        else:
            return 0.0

    def __repr__(self):
        return f"DiscreteSignal(name = '{self.name}', n = {self.start}..{self.end}, samples = {len(self)})"

    @property
    def indices(self):
        return self._indices

    @property
    def values(self):
        return self._values

    @property
    def start(self):
        return int(self._indices[0])

    @property
    def end(self):
        return int(self._indices[-1])

    def __len__(self):
        return int(self._indices.size)