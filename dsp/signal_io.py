from pathlib import Path

from dsp.discrete_signal import DiscreteSignal


def input_signal(filepath):
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError("File not found")

    with filepath.open("r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    if not lines:
        raise ValueError("File is empty")

    #   IF First line = number of samples

    try:
        first_value = int(lines[0])
    except ValueError:
        first_value = None

    if first_value is not None and first_value > 0:
        n = first_value

        if len(lines) - 1 != n:
            raise ValueError(
                f"Expected {n} samples, but found {len(lines) - 1}"
            )

        sample_lines = lines[1:]
    #Zeyad
    # First 3 lines are headers.
    # Samples start from line 4.
    elif len(lines) >= 4:
        sample_lines = lines[3:]

    else:
        raise ValueError("Invalid signal file format")

    indices = []
    values = []

    for line_number, line in enumerate(sample_lines, start=1):
        parts = line.split()

        if len(parts) != 2:
            raise ValueError(
                f"Invalid sample line: '{line}'"
            )

        try:
            index = float(parts[0])
            value = float(parts[1])
        except ValueError:
            raise ValueError(
                f"Invalid numeric value in sample line: '{line}'"
            )

        indices.append(index)
        values.append(value)

    if not indices:
        raise ValueError("Signal contains no samples")

    return DiscreteSignal(indices, values)


def output_signal(signal, filepath):
    filepath = Path(filepath)

    with filepath.open("w", encoding="utf-8") as file:
        file.write(f"{len(signal)}\n")

        for idx, val in zip(signal.indices, signal.values):
            file.write(f"{idx} {val}\n")