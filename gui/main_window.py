from __future__ import annotations
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget
from gui.panels import PANELS
from gui.signal_store import SignalStore

FILE_FORMAT_HELP = """\
Signal files are plain text:

    5            <- N, the number of samples
    -2 1.0       <- index  value
    -1 3.0
    0 2.0
    1 -1.0
    2 4.0

Indices are integers (they may be negative); values may be decimals.
"""

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DSP")
        self.resize(1200, 760)

        self.store = SignalStore()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        for panel_cls in PANELS:
            panel = panel_cls(self.store)
            panel.message.connect(lambda text: self.statusBar().showMessage(text, 5000))
            self.tabs.addTab(panel, panel_cls.title)

        self._build_menu()
        self.statusBar().showMessage("Ready")

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = self.menuBar().addMenu("&Help")
        fmt = QAction("Signal file &format", self)
        fmt.triggered.connect(
            lambda: QMessageBox.information(self, "Signal file format", FILE_FORMAT_HELP)
        )
        about = QAction("&About", self)
        about.triggered.connect(
            lambda: QMessageBox.about(
                self, "About", "DSP \nDigital Signal Processing course project."
            )
        )
        help_menu.addAction(fmt)
        help_menu.addAction(about)
