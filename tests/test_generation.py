import numpy as np
import pytest

from dsp.generation import generate_wave


def test_sine_wave_values():
    signal = generate_wave("sine", 2, 0, 1, 10)

    expected = 2 * np.sin(
        2 * np.pi * 1 * np.arange(10) / 10
    )

    assert np.array_equal(signal.indices, np.arange(10))
    assert np.allclose(signal.values, expected)


def test_cosine_wave_values():
    signal = generate_wave("cosine", 2, 0, 1, 10)

    expected = 2 * np.cos(
        2 * np.pi * 1 * np.arange(10) / 10
    )

    assert np.array_equal(signal.indices, np.arange(10))
    assert np.allclose(signal.values, expected)


def test_sample_count():
    signal = generate_wave("sine", 2, 0, 1, 10)

    assert len(signal.values) == 10


def test_invalid_wave_type():
    with pytest.raises(ValueError):
        generate_wave("triangle", 2, 0, 1, 10)


def test_invalid_sampling_frequency():
    with pytest.raises(ValueError):
        generate_wave("sine", 2, 0, 5, 10)


def test_invalid_duration():
    with pytest.raises(ValueError):
        generate_wave("sine", 2, 0, 1, 10, duration=0)
