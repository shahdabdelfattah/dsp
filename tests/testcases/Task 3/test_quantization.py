import numpy as np
import pytest

from dsp.discrete_signal import DiscreteSignal
from dsp.quantization import quantize


def test_test_case_1_expected_encoded_and_quantized_values():
    values = [0.387, 0.430, 0.478, 0.531, 0.590, 0.6561, 0.729, 0.81, 0.9, 1.0, 0.2]
    signal = DiscreteSignal(range(len(values)), values, name="Quan1")
    result = quantize(signal, bits=3)

    assert result.encoded == ["001", "010", "010", "011", "011", "100", "101", "110", "110", "111", "000"]
    assert np.allclose(result.quantized.values, [0.35, 0.45, 0.45, 0.55, 0.55, 0.65, 0.75, 0.85, 0.85, 0.95, 0.25])
    assert result.levels == 8
    assert result.bits == 3


def test_test_case_2_expected_all_outputs():
    values = [-1.22, 1.5, 3.24, 3.94, 2.20, -1.1, -2.26, -1.88, -1.2]
    signal = DiscreteSignal(range(len(values)), values, name="Quan2")
    result = quantize(signal, levels=4)

    assert result.interval_indices == [1, 3, 4, 4, 3, 1, 1, 1, 1]
    assert result.encoded == ["00", "10", "11", "11", "10", "00", "00", "00", "00"]
    assert np.allclose(result.quantized.values, [-1.485, 1.615, 3.165, 3.165, 1.615, -1.485, -1.485, -1.485, -1.485])
    assert np.allclose(result.error.values, [-0.265, 0.115, -0.075, -0.775, -0.585, -0.385, 0.775, 0.395, -0.285])


def test_levels_not_power_of_two_uses_enough_bits():
    signal = DiscreteSignal([0, 1, 2], [-1, 0, 1])
    result = quantize(signal, levels=3)
    assert result.levels == 3
    assert result.bits == 2
    assert result.encoded == ["00", "01", "10"]


def test_constant_signal_has_zero_error():
    signal = DiscreteSignal([0, 1, 2], [4.2, 4.2, 4.2])
    result = quantize(signal, levels=8)
    assert np.allclose(result.quantized.values, signal.values)
    assert np.allclose(result.error.values, 0)
    assert result.interval_indices == [1, 1, 1]
    assert result.encoded == ["000", "000", "000"]


@pytest.mark.parametrize("kwargs", [{}, {"levels": 4, "bits": 2}])
def test_requires_exactly_one_configuration(kwargs):
    signal = DiscreteSignal([0, 1], [0, 1])
    with pytest.raises(ValueError):
        quantize(signal, **kwargs)


@pytest.mark.parametrize("kwargs", [{"levels": 1}, {"levels": 2.5}, {"bits": 0}, {"bits": 1.5}])
def test_rejects_invalid_configuration(kwargs):
    signal = DiscreteSignal([0, 1], [0, 1])
    with pytest.raises(ValueError):
        quantize(signal, **kwargs)
