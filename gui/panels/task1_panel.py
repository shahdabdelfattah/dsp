
from __future__ import annotations
import re
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
    QGroupBox, QHBoxLayout, QInputDialog, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from dsp.discrete_signal import DiscreteSignal
from dsp.operations import add, subtract, multiply, delay, advance, fold
from dsp.signal_io import input_signal, output_signal
from gui.panels.base import TaskPanel
from gui.plot_widget import SignalPlot
from gui.signal_store import SignalStore


class Task1Panel(TaskPanel):
    title = "Task 1 \u2013 Signal basics"

    def __init__(self, store: SignalStore, parent=None) -> None:
        super().__init__(store, parent)
        self._publishing = False  
        self._build_ui()
        self.store.changed.connect(self._on_store_changed)
        self._refresh_views()

    def _build_ui(self) -> None:
        self.plot = SignalPlot()

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(self._build_signals_box())
        left_layout.addWidget(self._build_operations_box())
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

    def _build_signals_box(self) -> QGroupBox:
        box = QGroupBox("Signals  (select one or more)")
        layout = QVBoxLayout(box)

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.setToolTip("Double-click a signal to rename it")
        self.list.itemSelectionChanged.connect(self._plot_selection)
        self.list.itemDoubleClicked.connect(self._on_rename)
        layout.addWidget(self.list)

        row = QHBoxLayout()
        load = QPushButton("Load\u2026")
        load.setShortcut("Ctrl+O")
        load.clicked.connect(self._on_load)
        save = QPushButton("Save\u2026")
        save.clicked.connect(self._on_save)
        remove = QPushButton("Remove")
        remove.clicked.connect(self._on_remove)
        for b in (load, save, remove):
            row.addWidget(b)
        layout.addLayout(row)
        return box

    def _build_operations_box(self) -> QGroupBox:
        box = QGroupBox("Operations")
        form = QFormLayout(box)

        # Add
        add_btn = QPushButton("Add selected signals")
        add_btn.setToolTip("Sums two or more selected signals")
        add_btn.clicked.connect(self._on_add)
        form.addRow(add_btn)

        # Subtract
        self.combo_a, self.combo_b = QComboBox(), QComboBox()
        sub_row = QHBoxLayout()
        sub_row.addWidget(self.combo_a, 1)
        sub_row.addWidget(QLabel("\u2212"))
        sub_row.addWidget(self.combo_b, 1)
        form.addRow("Subtract", sub_row)
        sub_btn = QPushButton("Compute A \u2212 B")
        sub_btn.clicked.connect(self._on_subtract)
        form.addRow(sub_btn)

        # Multiply
        self.constant = QDoubleSpinBox()
        self.constant.setRange(-1e6, 1e6)
        self.constant.setDecimals(4)
        self.constant.setSingleStep(0.5)
        self.constant.setValue(2.0)
        form.addRow("Constant c", self.constant)
        mul_btn = QPushButton("Multiply selected by c")
        mul_btn.setToolTip("|c| > 1 amplifies, |c| < 1 reduces, c < 0 flips the sign")
        mul_btn.clicked.connect(self._on_multiply)
        form.addRow(mul_btn)

        # Delay / advance
        self.k = QSpinBox()
        self.k.setRange(0, 100000)
        self.k.setValue(1)
        form.addRow("Shift k (steps)", self.k)
        shift_row = QHBoxLayout()
        delay_btn = QPushButton("Delay  x(n\u2212k)")
        delay_btn.clicked.connect(self._on_delay)
        advance_btn = QPushButton("Advance  x(n+k)")
        advance_btn.clicked.connect(self._on_advance)
        shift_row.addWidget(delay_btn)
        shift_row.addWidget(advance_btn)
        form.addRow(shift_row)

        # Fold
        fold_btn = QPushButton("Fold  x(\u2212n)")
        fold_btn.clicked.connect(self._on_fold)
        form.addRow(fold_btn)

        hint = QLabel("Results are added to the list, so you can keep chaining operations.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: gray;")
        form.addRow(hint)
        return box

    @staticmethod
    def _describe(sig: DiscreteSignal) -> str:
        return f"{sig.name}    (n = {sig.start} \u2026 {sig.end},  {len(sig)} samples)"

    def _selected(self) -> list[DiscreteSignal]:
        rows = sorted(i.row() for i in self.list.selectedIndexes())
        signals = self.store.signals
        return [signals[r] for r in rows]

    def _refresh_views(self, keep: list[DiscreteSignal] = ()) -> None:
        prev_a, prev_b = self.combo_a.currentIndex(), self.combo_b.currentIndex()

        self.list.blockSignals(True)
        self.list.clear()
        for sig in self.store.signals:
            item = QListWidgetItem(self._describe(sig))
            self.list.addItem(item)
            if any(sig is k for k in keep):
                item.setSelected(True)
        self.list.blockSignals(False)

        names = [s.name for s in self.store.signals]
        for combo, prev, fallback in ((self.combo_a, prev_a, 0), (self.combo_b, prev_b, 1)):
            combo.clear()
            combo.addItems(names)
            if names:
                combo.setCurrentIndex(prev if 0 <= prev < len(names) else min(fallback, len(names) - 1))
        # A − B with A == B is pointless, so default B to a different signal.
        if len(names) > 1 and self.combo_a.currentIndex() == self.combo_b.currentIndex():
            self.combo_b.setCurrentIndex((self.combo_a.currentIndex() + 1) % len(names))

    def _on_store_changed(self) -> None:
        self._refresh_views(keep=self._selected())
        if not self._publishing:
            self._plot_selection()

    def _plot_selection(self) -> None:
        selected = self._selected()
        if selected:
            self.plot.show_signals(selected)
        else:
            self.plot.clear()

    def _warn(self, text: str, title: str = "Cannot do that") -> None:
        QMessageBox.warning(self, title, text)

    def _require(self, count: int | None = None, minimum: int | None = None) -> list[DiscreteSignal] | None:
        selected = self._selected()
        if count is not None and len(selected) != count:
            noun = "signal" if count == 1 else "signals"
            self._warn(f"Select exactly {count} {noun} first (you selected {len(selected)}).")
            return None
        if minimum is not None and len(selected) < minimum:
            self._warn(f"Select at least {minimum} signals first (you selected {len(selected)}).")
            return None
        return selected

    def _publish(self, inputs: list[DiscreteSignal], result: DiscreteSignal) -> None:
        self._publishing = True
        try:
            self.store.add(result)
        finally:
            self._publishing = False
        self._refresh_views(keep=[result])
        self.plot.show_operation(inputs, result)
        self.message.emit(f"Created: {result.name}")

    def _run(self, inputs: list[DiscreteSignal], compute) -> None:
        try:
            result = compute()
        except ValueError as exc:
            self._warn(str(exc))
            return
        self._publish(inputs, result)

    def _on_load(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Load signal files", "", "Text files (*.txt);;All files (*)"
        )
        errors = []
        loaded = []
        for path in paths:
            try:
                loaded.append(self.store.add(input_signal(path)))
            except:
                errors.append("The file is not a valid signal")
        if errors:
            self._warn("\n\n".join(errors), "Could not load some files")
        if loaded:
            self._refresh_views(keep=loaded)
            self._plot_selection()
            self.message.emit(f"Loaded {len(loaded)} signal(s)")

    def _on_save(self) -> None:
        selected = self._require(count=1)
        if not selected:
            return
        sig = selected[0]
        safe = re.sub(r"[^\w.\-]+", "_", sig.name).strip("_") or "signal"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save signal", f"{safe}.txt", "Text files (*.txt)"
        )
        if not path:
            return
        try:
            output_signal(sig, path)
        except OSError as exc:
            self._warn(f"Could not save the file: {exc.strerror or exc}")
            return
        self.message.emit(f"Saved {Path(path).name}")

    def _on_remove(self) -> None:
        selected = self._require(minimum=1)
        if selected:
            self.store.remove(selected)

    def _on_rename(self, item: QListWidgetItem) -> None:
        sig = self.store.signals[self.list.row(item)]
        new_name, ok = QInputDialog.getText(self, "Rename signal", "New name:", text=sig.name)
        if ok:
            try:
                self.store.rename(sig, new_name)
            except ValueError as exc:
                self._warn(str(exc))

    def _on_add(self) -> None:
        selected = self._require(minimum=2)
        if selected:
            self._run(selected, lambda: add(selected))

    def _on_subtract(self) -> None:
        signals = self.store.signals
        a_i, b_i = self.combo_a.currentIndex(), self.combo_b.currentIndex()
        if len(signals) < 1 or a_i < 0 or b_i < 0:
            self._warn("Load a signal first.")
            return
        a, b = signals[a_i], signals[b_i]
        self._run([a, b], lambda: subtract(a, b))

    def _on_multiply(self) -> None:
        selected = self._require(count=1)
        if selected:
            c = self.constant.value()
            self._run(selected, lambda: multiply(selected[0], c))

    def _on_delay(self) -> None:
        selected = self._require(count=1)
        if selected:
            self._run(selected, lambda: delay(selected[0], self.k.value()))

    def _on_advance(self) -> None:
        selected = self._require(count=1)
        if selected:
            self._run(selected, lambda: advance(selected[0], self.k.value()))

    def _on_fold(self) -> None:
        selected = self._require(count=1)
        if selected:
            self._run(selected, lambda: fold(selected[0]))
