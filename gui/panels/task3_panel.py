from __future__ import annotations

import re
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QRadioButton, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from dsp.discrete_signal import DiscreteSignal
from dsp.quantization import QuantizationResult, quantize
from dsp.signal_io import input_signal, output_signal
from gui.panels.base import TaskPanel
from gui.plot_widget import SignalPlot
from gui.quantization_table import QuantizationTable
from gui.signal_store import SignalStore

LEVELS_RANGE = (2, 65536)
BITS_RANGE = (1, 16)
DEFAULT_LEVELS = 4
DEFAULT_BITS = 3


class Task3Panel(TaskPanel):
    title = "Task 3"

    def __init__(self, store: SignalStore, parent=None) -> None:
        super().__init__(store, parent)
        self._last_result: tuple[DiscreteSignal, QuantizationResult] | None = None
        self._build_ui()
        self.store.changed.connect(self._refresh_choices)
        self._refresh_choices()
        self._update_readout()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        self.plot = SignalPlot()
        self.table = QuantizationTable()

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(self._build_signal_box())
        left_layout.addWidget(self._build_settings_box())
        left_layout.addWidget(self._build_quantize_box())
        left_layout.addStretch(1)
        left.setMinimumWidth(400)
        left.setMaximumWidth(440)

        results = QSplitter(Qt.Vertical)
        results.addWidget(self.plot)
        results.addWidget(self.table)
        results.setStretchFactor(0, 3)
        results.setStretchFactor(1, 2)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(results)
        splitter.setStretchFactor(1, 1)
        splitter.setChildrenCollapsible(False)

        root = QHBoxLayout(self)
        root.addWidget(splitter)

    def _build_signal_box(self) -> QGroupBox:
        box = QGroupBox("Signal to quantize")
        box.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(box)
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self._selection_changed)
        layout.addWidget(self.combo)

        self.load_button = QPushButton("Load signal from file...")
        self.load_button.clicked.connect(self._on_load)
        layout.addWidget(self.load_button)
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

        self.radio_levels.toggled.connect(self._on_kind_changed)
        self.amount.valueChanged.connect(self._settings_changed)
        self.radio_bits.toggled.connect(self._settings_changed)
        return box

    def _build_quantize_box(self) -> QGroupBox:
        box = QGroupBox("Quantize")
        box.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(box)

        self.quantize_button = QPushButton("Quantize")
        self.quantize_button.clicked.connect(self._quantize_selected)
        layout.addWidget(self.quantize_button)

        self.radio_discrete = QRadioButton("Discrete (stem)")
        self.radio_continuous = QRadioButton("Continuous (line)")
        self.radio_continuous.setChecked(True)
        layout.addWidget(self.radio_discrete)
        layout.addWidget(self.radio_continuous)
        self.radio_discrete.toggled.connect(self._on_plot_mode_changed)
        self.radio_continuous.toggled.connect(self._on_plot_mode_changed)

        self.save_button = QPushButton("Save result to file...")
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)
        return box

    # ------------------------------------------------------ settings logic
    @property
    def levels(self) -> int:
        n = self.amount.value()
        return 2 ** n if self.radio_bits.isChecked() else n

    @property
    def bits(self) -> int:
        n = self.amount.value()
        return n if self.radio_bits.isChecked() else (n - 1).bit_length()

    def _on_kind_changed(self) -> None:
        if self.radio_bits.isChecked():
            self.amount.setRange(*BITS_RANGE)
            self.amount.setValue(DEFAULT_BITS)
        else:
            self.amount.setRange(*LEVELS_RANGE)
            self.amount.setValue(DEFAULT_LEVELS)
        self._settings_changed()

    def _settings_changed(self, *_args) -> None:
        self._update_readout()
        self._clear_result()

    def _update_readout(self) -> None:
        if self.radio_bits.isChecked():
            self.readout.setText(f"{self.bits} bits  →  {self.levels} levels")
        else:
            self.readout.setText(f"{self.levels} levels  →  {self.bits} bits per sample")

    # --------------------------------------------------------- signal list
    @staticmethod
    def _select(combo: QComboBox, sig: DiscreteSignal | None) -> bool:
        for i in range(combo.count()):
            if combo.itemData(i) is sig:
                combo.setCurrentIndex(i)
                return True
        return False

    def _refresh_choices(self) -> None:
        previous = self.combo.currentData()
        self.combo.blockSignals(True)
        self.combo.clear()
        for sig in self.store.signals:
            self.combo.addItem(sig.name, sig)
        if previous is None or not self._select(self.combo, previous):
            self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)
        self.quantize_button.setEnabled(self.combo.currentData() is not None)
        self._clear_result()

    def _selection_changed(self, *_args) -> None:
        self.quantize_button.setEnabled(self.combo.currentData() is not None)
        self._clear_result()

    def _clear_result(self) -> None:
        self._last_result = None
        self._render_result()
        self.table.clear_result()
        self.save_button.setEnabled(False)

    @property
    def plot_mode(self) -> str:
        return "continuous" if self.radio_continuous.isChecked() else "discrete"

    def _on_plot_mode_changed(self, checked: bool) -> None:
        if checked:
            self._render_result()

    def _render_result(self) -> None:
        if self._last_result is None:
            signal = self.combo.currentData()
            if signal is None:
                self.plot.clear()
            else:
                self.plot.show_signals([signal], mode=self.plot_mode)
            return
        signal, result = self._last_result
        self.plot.show_quantization(
            signal, result.quantized, result.error, mode=self.plot_mode
        )

    def _quantize_selected(self) -> None:
        sig = self.combo.currentData()
        if sig is None:
            return
        try:
            if self.radio_bits.isChecked():
                result = quantize(sig, bits=self.amount.value())
            else:
                result = quantize(sig, levels=self.amount.value())
        except (TypeError, ValueError, OverflowError) as exc:
            QMessageBox.warning(self, "Quantization error", str(exc))
            return

        self._last_result = (sig, result)
        self._render_result()
        self.table.show_result(sig, result)
        self.save_button.setEnabled(True)
        self.message.emit(
            f"Quantized {sig.name}: {result.levels} levels, {result.bits} bits/sample"
        )

    def _on_load(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load signal", "", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return
        try:
            signal = self.store.add(input_signal(path))
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Could not load signal", str(exc))
            return
        self._select(self.combo, signal)
        self.message.emit(f"Loaded {signal.name}")

    def _on_save(self) -> None:
        if self._last_result is None:
            return
        signal, result = self._last_result
        safe_name = re.sub(r"[^\w.\-]+", "_", signal.name).strip("_") or "signal"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save quantized signal",
            f"Quantized_{safe_name}.txt",
            "Text files (*.txt)",
        )
        if not path:
            return
        try:
            output_signal(result.quantized, path)
        except OSError as exc:
            QMessageBox.warning(
                self, "Could not save result", exc.strerror or str(exc)
            )
            return
        self.message.emit(f"Saved {Path(path).name}")
