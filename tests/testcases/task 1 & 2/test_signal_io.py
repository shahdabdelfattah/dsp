import numpy as np

from dsp.discrete_signal import DiscreteSignal
from dsp.signal_io import input_signal, output_signal


def test_output_signal_preserves_fractional_values(tmp_path):
    signal = DiscreteSignal([-1, 0], [1.25, -2.75], name="fractional")
    path = tmp_path / "signal.txt"

    output_signal(signal, path)
    loaded = input_signal(path)

    assert np.array_equal(loaded.indices, signal.indices)
    assert np.array_equal(loaded.values, signal.values)
