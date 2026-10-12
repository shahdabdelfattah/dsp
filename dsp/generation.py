
import numpy as np

from dsp.discrete_signal import DiscreteSignal


def generate_wave(
    Type,
    amplitude : float,
    theta : float,
    f : float,
    FS: float,
    duration : float=1.0,
    name=None,
) -> DiscreteSignal:
    
    if Type not in ("sine", "cosine"):
        raise ValueError(" Type must be 'sine' or 'cosine'.")


    try:
        amplitude = float(amplitude)
        theta = float(theta)
        f = float(f)
        FS = float(FS)
        duration = float(duration)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("All parameters must be numbers.")

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

    #  Check the sampling theorem
    if FS <= 2 * f:
        raise ValueError("Sampling frequency must be greater than 2 * frequency.")

    #  Calculate the number of samples
    sample_count = round(duration * FS)

    if sample_count < 1:
        raise ValueError("Duration is too short to produce a sample.")

    indices = np.arange(sample_count)
    
    #  Calculate the time values for each sample
    T = indices / FS
    angles = (  2 * np.pi * f * T  + theta  )

    # 7. Calculate the sample values
    if Type == "sine":
        values = amplitude * np.sin(angles)
    else:
        values = amplitude * np.cos(angles)


    if name is None:
        name = f"{Type.capitalize()} Wave"

    return DiscreteSignal(indices, values, name=name)
