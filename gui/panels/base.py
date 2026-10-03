from __future__ import annotations
from PySide6.QtCore import Signal as QtSignal
from PySide6.QtWidgets import QWidget
from gui.signal_store import SignalStore

class TaskPanel(QWidget):
    title = "Task"
    message = QtSignal(str)

    def __init__(self, store: SignalStore, parent=None) -> None:
        super().__init__(parent)
        self.store = store
