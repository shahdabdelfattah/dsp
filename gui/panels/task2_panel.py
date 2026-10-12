from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from dsp.discrete_signal import DiscreteSignal
from dsp.generation import generate_wave
from gui.generator_dialog import GeneratorDialog
from gui.panels.base import TaskPanel
from gui.plot_widget import SignalPlot
from gui.signal_store import SignalStore


NONE_LABEL = "(none)"


class Task2Panel(TaskPanel):
    title = "Task 2"

    def __init__(self, store: SignalStore, parent=None) -> None:
        super().__init__(store, parent)
        self._build_ui()
        self.store.changed.connect(self._refresh_choices)
        self._refresh_choices()

    def _build_ui(self) -> None:
        self.plot = SignalPlot()

        left = QWidget()
        left_layout = QVBoxLayout(left)

        left_layout.addWidget(self._build_generation_box())

        left_layout.addWidget(self._build_signals_box())

        left_layout.addWidget(self._build_representation_box())

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

    def _build_generation_box(self) -> QGroupBox:
        box = QGroupBox("Signal Generation")
        box.setStyleSheet("QGroupBox { font-weight: bold; }")

        layout = QVBoxLayout(box)

        self.generate_button = QPushButton("Generate Signal")
        self.generate_button.clicked.connect(self._generate_signal)

        layout.addWidget(self.generate_button)

        return box

    def _build_signals_box(self) -> QGroupBox:
        box = QGroupBox("Signals to display")
        box.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(box)

        self.combo_1 = QComboBox()
        self.combo_2 = QComboBox()

        for label, combo in (
            ("Signal 1", self.combo_1),
            ("Signal 2", self.combo_2),
        ):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(combo, 1)
            layout.addLayout(row)

            combo.currentIndexChanged.connect(self._update_plot)

        self.overlay_check = QCheckBox("Overlay both in one plot")
        self.overlay_check.setChecked(True)
        self.overlay_check.toggled.connect(self._update_plot)

        layout.addWidget(self.overlay_check)

        return box

    def _build_representation_box(self) -> QGroupBox:
        box = QGroupBox("Representation")
        box.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(box)

        self.radio_discrete = QRadioButton("Discrete (stem)")
        self.radio_continuous = QRadioButton("Continuous (line)")

        self.radio_discrete.setChecked(True)

        for radio in (
            self.radio_discrete,
            self.radio_continuous,
        ):
            radio.toggled.connect(self._update_plot)
            layout.addWidget(radio)

        return box

   
    def _generate_signal(self) -> None:
        dialog = GeneratorDialog(self)

        if dialog.exec() != GeneratorDialog.DialogCode.Accepted:
            return

        params = dialog.get_parameters()

        try:
            signal = generate_wave(**params)

            self.store.add(signal)

            self._select(self.combo_1, signal)

            self._update_plot()

            self.message.emit(
                f"Generated {signal.name} successfully"
            )

        except (ValueError, TypeError) as error:
            QMessageBox.warning(
                self,
                "Signal Generation Error",
                str(error),
            )

 
    @property
    def mode(self) -> str:
        return (
            "continuous"
            if self.radio_continuous.isChecked()
            else "discrete"
        )

    @staticmethod
    def _select(
        combo: QComboBox,
        sig: DiscreteSignal | None,
    ) -> bool:
        """Select the item holding exactly sig. Returns False if absent."""
        for i in range(combo.count()):
            if combo.itemData(i) is sig:
                combo.setCurrentIndex(i)
                return True

        return False

    def _refresh_choices(self) -> None:
        """Refill both dropdowns while preserving the user's selections."""
        prev_1 = self.combo_1.currentData()
        prev_2 = self.combo_2.currentData()

        signals = self.store.signals

        for combo in (self.combo_1, self.combo_2):
            combo.blockSignals(True)
            combo.clear()

        self.combo_2.addItem(NONE_LABEL, None)

        for sig in signals:
            self.combo_1.addItem(sig.name, sig)
            self.combo_2.addItem(sig.name, sig)

        if prev_1 is None or not self._select(
            self.combo_1, prev_1
        ):
            self.combo_1.setCurrentIndex(0)

        if prev_2 is not None:
            self._select(self.combo_2, prev_2)

        for combo in (self.combo_1, self.combo_2):
            combo.blockSignals(False)

        self._update_plot()

    def _chosen_signals(self) -> list[DiscreteSignal]:
        chosen: list[DiscreteSignal] = []

        for sig in (
            self.combo_1.currentData(),
            self.combo_2.currentData(),
        ):
            if sig is not None and not any(
                sig is existing for existing in chosen
            ):
                chosen.append(sig)

        return chosen

    def _update_plot(self) -> None:
        chosen = self._chosen_signals()

        if chosen:
            self.plot.show_signals(
                chosen,
                mode=self.mode,
                overlay=self.overlay_check.isChecked(),
            )
        else:
            self.plot.clear()
