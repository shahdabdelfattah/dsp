from dsp.discrete_signal import DiscreteSignal
from pathlib import Path


def input_signal(filepath):
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found")

    with filepath.open("r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    if not lines:
        raise ValueError("File is empty")

    try:
        n = int(lines[0])
    except ValueError:
        raise ValueError("First line must contain the number of samples")

    if n <= 0:
        raise ValueError("Number of samples must be greater than zero")

    if len(lines) - 1 != n:
        raise ValueError(
            f"Expected {n} samples, but found {len(lines) - 1}"
        )

    indices = []
    values = []

    for line_number, line in enumerate(lines[1:], start=2):
        parts = line.split()

        if len(parts) != 2:
            raise ValueError(
                f"Line {line_number} must contain exactly two values"
            )

        try:
            index = float(parts[0])
            value = float(parts[1])
        except ValueError:
            raise ValueError(
                f"Invalid numeric value on line {line_number}"
            )

        indices.append(index)
        values.append(value)

    return DiscreteSignal(indices, values)


def output_signal(signal, filepath):
    filepath = Path(filepath)

    with filepath.open("w", encoding="utf-8") as file:
        file.write(f"{len(signal)}\n")

        for idx, val in zip(signal.indices, signal.values):
            file.write(f"{idx} {val}\n")