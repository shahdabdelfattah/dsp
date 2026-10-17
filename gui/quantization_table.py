from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView

HEADERS = ["n", "Original", "Interval", "Encoded", "Quantized", "Error"]


class _ResultModel(QAbstractTableModel):
    """Read-only table model: rows are read straight from the signals."""

    def __init__(self) -> None:
        super().__init__()
        self._original = None
        self._result = None

    def set_result(self, original, result) -> None:
        self.beginResetModel()
        self._original, self._result = original, result
        self.endResetModel()

    def clear(self) -> None:
        self.set_result(None, None)

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if self._original is None else len(self._original)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignCenter)
        if role != Qt.DisplayRole:
            return None

        row, col = index.row(), index.column()
        if col == 0:
            return str(self._original.indices[row])
        if col == 1:
            return f"{self._original.values[row]:.4f}"
        if col == 2:
            return str(self._result.interval_indices[row])
        if col == 3:
            return self._result.encoded[row]
        if col == 4:
            return f"{self._result.quantized.values[row]:.4f}"
        return f"{self._result.error.values[row]:.4f}"

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return HEADERS[section]
        return None


class QuantizationTable(QTableView):
    """Shows n, original, interval index, binary code, quantized value, error."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._model = _ResultModel()
        self.setModel(self._model)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def show_result(self, original, result) -> None:
        self._model.set_result(original, result)

    def clear_result(self) -> None:
        self._model.clear()