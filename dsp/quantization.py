from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from dsp.discrete_signal import DiscreteSignal


@dataclass(frozen=True)
class QuantizationResult:
    quantized: DiscreteSignal
    error: DiscreteSignal
    encoded: list[str]
    interval_indices: list[int]
    levels: int
    bits: int


def quantize(
    signal: DiscreteSignal,
    *,
    levels: int | None = None,
    bits: int | None = None,
) -> QuantizationResult:

    if (levels is None) == (bits is None):
        raise ValueError("Provide exactly one of 'levels' or 'bits'.")

    if bits is not None:
        if isinstance(bits, bool) or not isinstance(bits, (int, np.integer)) or bits < 1:
            raise ValueError("bits must be a positive integer.")
        resolved_bits = int(bits)
        resolved_levels = 2 ** resolved_bits
    else:
        if isinstance(levels, bool) or not isinstance(levels, (int, np.integer)) or levels < 2:
            raise ValueError("levels must be an integer greater than or equal to 2.")
        resolved_levels = int(levels)
        resolved_bits = math.ceil(math.log2(resolved_levels))

    values = signal.values
    low = float(np.min(values))
    high = float(np.max(values))
    width = high - low

    if width == 0.0:
        interval_zero_based = np.zeros(len(signal), dtype=int)
        quantized_values = values.copy()
        errors = np.zeros(len(signal), dtype=float)
    else:
        delta = width / resolved_levels
        interval_zero_based = np.floor((values - low) / delta).astype(int)
        # The maximum value belongs to the final interval, not level L.
        interval_zero_based = np.clip(interval_zero_based, 0, resolved_levels - 1)
        quantized_values = low + (interval_zero_based + 0.5) * delta
        errors = quantized_values - values

    encoded = [format(int(index), f"0{resolved_bits}b") for index in interval_zero_based]
    # Course output files number intervals from 1; binary codes use index 0..L-1.
    interval_indices = [int(index) + 1 for index in interval_zero_based]
    quantized = DiscreteSignal(signal.indices, quantized_values, name=f"Quantized({signal.name})")
    error = DiscreteSignal(signal.indices, errors, name=f"Error({signal.name})")

    return QuantizationResult(
        quantized=quantized,
        error=error,
        encoded=encoded,
        interval_indices=interval_indices,
        levels=resolved_levels,
        bits=resolved_bits,
    )
