
import numpy as np

from dsp.discrete_signal import DiscreteSignal


def generate_wave(
    Type,
    amplitude : float,
    theta   : float,
    f   : float,
    FS : float,
    duration : float=1.0,
    name=None,
) -> DiscreteSignal:
    """Generate a discrete sine or cosine wave."""

    # # 1. Convert numeric inputs to floats
    # amplitude = float(amplitude)
    # theta = float(theta)
    # f = float(f)
    # FS = float(FS)
    # duration = float(duration)
    
    # 1. Check that the wave type is valid
    if Type not in ("sine", "cosine"):
        raise ValueError("kind must be 'sine' or 'cosine'.")

    # 2. Check that all parameters are finite numbers
    if not all(np.isfinite(v) for v in (
        amplitude, theta, f, FS, duration
    )):
        raise ValueError("All parameters must be finite numbers.")

    if f <= 0:
        raise ValueError("Frequency must be positive.")

    if FS <= 0:
        raise ValueError("Sampling frequency must be positive.")

    if duration <= 0:
        raise ValueError("Duration must be positive.")

    # 3. Check the sampling theorem
    if FS <= 2 * f:
        raise ValueError("Sampling frequency must be greater than 2 * frequency.")

    # 4. Calculate the number of samples
    sample_count = round(duration * FS)

    if sample_count < 1:
        raise ValueError("Duration is too short to produce a sample.")

    # 5. Generate the sample indices
    indices = np.arange(sample_count)

    # 6. Calculate the angle for each sample
    n = indices / FS
    angles = (  2 * np.pi * f * n  + theta  )

    # 7. Calculate the sample values
    if Type == "sine":
        values = amplitude * np.sin(angles)
    else:
        values = amplitude * np.cos(angles)

    # 8. Return a DiscreteSignal
    if name is None:
        name = f"{Type.capitalize()} Wave"

    return DiscreteSignal(indices, values, name=name)
