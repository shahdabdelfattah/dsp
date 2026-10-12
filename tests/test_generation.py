
import numpy as np
import pytest

from dsp.generation import generate_wave


def test_sine_wave_values():
    signal = generate_wave("sine", 2, 0, 1, 10)
    expected = 2 * np.sin(2 * np.pi * np.arange(10) / 10)

    assert np.array_equal(signal.indices, np.arange(10))
    assert np.allclose(signal.values, expected)


def test_cosine_wave_values():
    signal = generate_wave("cosine", 2, 0, 1, 10)
    expected = 2 * np.cos(2 * np.pi * np.arange(10) / 10)

    assert np.array_equal(signal.indices, np.arange(10))
    assert np.allclose(signal.values, expected)


def test_sample_count():
    signal = generate_wave("sine", 2, 0, 1, 10, duration=2)

    assert len(signal) == 20


def test_continuous_wave_preserves_generation_parameters():
    signal = generate_wave("sine", 2, 0.3, 1, 10, duration=2)
    times = np.array([0.0, 0.25, 1.0, 2.0])
    expected = 2 * np.sin(2 * np.pi * times + 0.3)

    assert signal.continuous_wave.duration == 2
    assert np.allclose(signal.continuous_wave.values_at(times), expected)


def test_amplitude_is_applied():
    signal = generate_wave("sine", 3, 0, 1, 20)

    assert np.max(signal.values) == pytest.approx(3)
    assert np.min(signal.values) == pytest.approx(-3)


def test_phase_shift_is_applied():
    theta = np.pi / 2
    signal = generate_wave("sine", 1, theta, 1, 10)

    assert signal.values[0] == pytest.approx(1)


def test_zero_amplitude():
    signal = generate_wave("sine", 0, 0, 1, 10)

    assert np.allclose(signal.values, 0)


# Invalid wave types

@pytest.mark.parametrize("wave_type", [
    "triangle",
    "square",
    "",
    None,
])
def test_invalid_wave_type(wave_type):
    with pytest.raises(ValueError):
        generate_wave(wave_type, 1, 0, 1, 10)


# Invalid numeric parameters

@pytest.mark.parametrize("parameter,value", [
    ("amplitude", "abc"),
    ("theta", "abc"),
    ("f", "abc"),
    ("FS", "abc"),
    ("duration", "abc"),
])
def test_nonnumeric_parameters(parameter, value):
    params = {
        "Type": "sine",
        "amplitude": 1,
        "theta": 0,
        "f": 1,
        "FS": 10,
        "duration": 1,
    }
    params[parameter] = value

    with pytest.raises(ValueError):
        generate_wave(**params)


@pytest.mark.parametrize("parameter,value", [
    ("amplitude", np.nan),
    ("theta", np.inf),
    ("f", np.inf),
    ("FS", np.nan),
    ("duration", np.inf),
])
def test_nonfinite_parameters(parameter, value):
    params = {
        "Type": "sine",
        "amplitude": 1,
        "theta": 0,
        "f": 1,
        "FS": 10,
        "duration": 1,
    }
    params[parameter] = value

    with pytest.raises(ValueError):
        generate_wave(**params)


# Frequency and sampling theorem

@pytest.mark.parametrize("frequency", [0, -1, -10])
def test_invalid_signal_frequency(frequency):
    with pytest.raises(ValueError):
        generate_wave("sine", 1, 0, frequency, 20)


@pytest.mark.parametrize("sampling_frequency", [0, -1, 2, 10])
def test_invalid_sampling_frequency(sampling_frequency):
    with pytest.raises(ValueError):
        generate_wave("sine", 1, 0, 5, sampling_frequency)


def test_sampling_frequency_must_exceed_twice_signal_frequency():
    with pytest.raises(ValueError):
        generate_wave("sine", 1, 0, 5, 10)


def test_valid_sampling_frequency_above_nyquist_limit():
    signal = generate_wave("sine", 1, 0, 4, 10)

    assert len(signal) == 10
    assert np.all(np.isfinite(signal.values))


# Invalid duration

@pytest.mark.parametrize("duration", [0, -1, -0.5])
def test_invalid_duration(duration):
    with pytest.raises(ValueError):
        generate_wave("sine", 1, 0, 1, 10, duration=duration)


def test_duration_too_short_to_produce_sample():
    with pytest.raises(ValueError):
        generate_wave("sine", 1, 0, 1, 10, duration=0.01)
