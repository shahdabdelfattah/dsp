from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QGroupBox, QHBoxLayout, QLabel, QRadioButton, QSpinBox,
    QSplitter, QVBoxLayout, QWidget,
)

from dsp.discrete_signal import DiscreteSignal
from gui.panels.base import TaskPanel
from gui.plot_widget import SignalPlot
from gui.signal_store import SignalStore

LEVELS_RANGE = (2, 65536)
BITS_RANGE = (1, 16)
DEFAULT_LEVELS = 8
DEFAULT_BITS = 3


class Task3Panel(TaskPanel):
    title = "Task 3"

    def __init__(self, store: SignalStore, parent=None) -> None:
        super().__init__(store, parent)
        self._build_ui()
        self.store.changed.connect(self._refresh_choices)
        self._refresh_choices()
        self._update_readout()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        self.plot = SignalPlot()

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(self._build_signal_box())
        left_layout.addWidget(self._build_settings_box())
        left_layout.addStretch(1)
        left.setMinimumWidth(340)
        left.setMaximumWidth(440)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(self.plot)
        splitter.setStretchFactor(1, 1)
        splitter.setChildrenCollapsible(False)

        root = QHBoxLayout(self)
        root.addWidget(splitter)

    def _build_signal_box(self) -> QGroupBox:
        box = QGroupBox("Signal to quantize")
        box.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(box)
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self._update_plot)
        layout.addWidget(self.combo)
        return box

    def _build_settings_box(self) -> QGroupBox:
        box = QGroupBox("Quantization settings")
        box.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(box)

        self.radio_levels = QRadioButton("Number of levels")
        self.radio_bits = QRadioButton("Number of bits")
        self.radio_levels.setChecked(True)
        layout.addWidget(self.radio_levels)
        layout.addWidget(self.radio_bits)

        self.amount = QSpinBox()
        self.amount.setRange(*LEVELS_RANGE)
        self.amount.setValue(DEFAULT_LEVELS)
        layout.addWidget(self.amount)

        self.readout = QLabel()
        self.readout.setStyleSheet("color: gray;")
        layout.addWidget(self.readout)

        # Only one radio needs a connection: when the other one is chosen,
        # this one toggles off, so it fires exactly once per switch.
        self.radio_levels.toggled.connect(self._on_kind_changed)
        self.amount.valueChanged.connect(self._update_readout)
        return box

    # ------------------------------------------------------ settings logic
    @property
    def levels(self) -> int:
        """Number of quantization levels the user asked for."""
        n = self.amount.value()
        return 2 ** n if self.radio_bits.isChecked() else n

    @property
    def bits(self) -> int:
        """Bits per sample needed to encode ``levels``."""
        n = self.amount.value()
        return n if self.radio_bits.isChecked() else (n - 1).bit_length()

    def _on_kind_changed(self) -> None:
        if self.radio_bits.isChecked():
            self.amount.setRange(*BITS_RANGE)
            self.amount.setValue(DEFAULT_BITS)
        else:
            self.amount.setRange(*LEVELS_RANGE)
            self.amount.setValue(DEFAULT_LEVELS)
        self._update_readout()

    def _update_readout(self) -> None:
        if self.radio_bits.isChecked():
            self.readout.setText(f"{self.bits} bits  \u2192  {self.levels} levels")
        else:
            self.readout.setText(f"{self.levels} levels  \u2192  {self.bits} bits per sample")

    # --------------------------------------------------------- signal list
    @staticmethod
    def _select(combo: QComboBox, sig: DiscreteSignal | None) -> bool:
        for i in range(combo.count()):
            if combo.itemData(i) is sig:
                combo.setCurrentIndex(i)
                return True
        return False

    def _refresh_choices(self) -> None:
        """Refill the dropdown from the store, keeping the user's pick."""
        previous = self.combo.currentData()
        self.combo.blockSignals(True)
        self.combo.clear()
        for sig in self.store.signals:
            self.combo.addItem(sig.name, sig)
        if previous is None or not self._select(self.combo, previous):
            self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)
        self._update_plot()

    def _update_plot(self) -> None:
        sig = self.combo.currentData()
        if sig is None:
            self.plot.clear()
        else:
            self.plot.show_signals([sig])