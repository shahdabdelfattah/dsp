from __future__ import annotations
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal as QtSignal

from dsp.discrete_signal import DiscreteSignal

class SignalStore(QObject):
    changed = QtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._signals: list[DiscreteSignal] = []

    @property
    def signals(self) -> tuple[DiscreteSignal, ...]:
        return tuple(self._signals)

    def _unique_name(self, base: str, ignore: DiscreteSignal | None = None) -> str:
        taken = {s.name for s in self._signals if s is not ignore}
        if base not in taken:
            return base
        counter = 2
        while f"{base} ({counter})" in taken:
            counter += 1
        return f"{base} ({counter})"

    def add(self, sig: DiscreteSignal) -> DiscreteSignal:
        sig.name = self._unique_name(sig.name)
        self._signals.append(sig)
        self.changed.emit()
        return sig

    def remove(self, sigs) -> None:
        doomed = {id(s) for s in sigs}
        self._signals = [s for s in self._signals if id(s) not in doomed]
        self.changed.emit()

    def rename(self, sig: DiscreteSignal, new_name: str) -> None:
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("the name cannot be empty")
        sig.name = self._unique_name(new_name, ignore=sig)
        self.changed.emit()
