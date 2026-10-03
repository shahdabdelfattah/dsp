from __future__ import annotations
from dsp.discrete_signal import DiscreteSignal


def _result_name(operation: str, signals: list[DiscreteSignal]) -> str:

    names = [signal.name for signal in signals]
    return f"{operation}({', '.join(names)})"


def add(signals: list[DiscreteSignal]) -> DiscreteSignal:
    if not signals:
        raise ValueError("At least one signal is required.")

    if len(signals) < 2:
        raise ValueError("At least two signals are required for addition.")

    all_indices = sorted(
        set(
            index
            for signal in signals
            for index in signal.indices
        )
    )

    result_values = [
        sum(signal.value_at(index) for signal in signals)
        for index in all_indices
    ]

    return DiscreteSignal(
        all_indices,
        result_values,
        name=_result_name("Add", signals),
    )


def subtract(
    signal_a: DiscreteSignal,
    signal_b: DiscreteSignal,
) -> DiscreteSignal:

    all_indices = sorted(
        set(signal_a.indices) | set(signal_b.indices)
    )

    result_values = [
        signal_a.value_at(index) - signal_b.value_at(index)
        for index in all_indices
    ]

    return DiscreteSignal(
        all_indices,
        result_values,
        name=f"{signal_a.name} - {signal_b.name}",
    )


def multiply(
    signal: DiscreteSignal,
    constant: float,
) -> DiscreteSignal:

    constant = float(constant)

    result_values = signal.values * constant

    return DiscreteSignal(
        signal.indices,
        result_values,
        name=f"{constant:g}*{signal.name}",
    )


def delay(
    signal: DiscreteSignal,
    k: int,
) -> DiscreteSignal:

    k = int(k)

    if k < 0:
        raise ValueError("Delay k must be non-negative.")

    new_indices = signal.indices + k

    return DiscreteSignal(
        new_indices,
        signal.values,
        name=f"Delay({signal.name}, {k})",
    )


def advance(
    signal: DiscreteSignal,
    k: int,
) -> DiscreteSignal:
    k = int(k)

    if k < 0:
        raise ValueError("Advance k must be non-negative.")

    new_indices = signal.indices - k

    return DiscreteSignal(
        new_indices,
        signal.values,
        name=f"Advance({signal.name}, {k})",
    )


def fold(signal: DiscreteSignal) -> DiscreteSignal:
    new_indices = -signal.indices
    return DiscreteSignal(
        new_indices,
        signal.values,
        name=f"Fold({signal.name})",
    )