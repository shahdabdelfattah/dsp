from __future__ import annotations
from dataclasses import dataclass
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PySide6.QtWidgets import QVBoxLayout, QWidget

from dsp import DiscreteSignal

INPUT_COLOR = "#1f77b4"
RESULT_COLOR = "#d62728"


@dataclass
class PlotItem:
    label: str
    signal: DiscreteSignal
    is_result: bool = False


class SignalPlot(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.figure = Figure(layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)
        self.clear()

    def clear(self) -> None:
        self.draw_items([])

    def show_signals(self, signals) -> None:
        self.draw_items([PlotItem(s.name, s) for s in signals])

    def show_operation(self, inputs, result: DiscreteSignal) -> None:
        items = [PlotItem(f"Input: {s.name}", s) for s in inputs]
        items.append(PlotItem(f"Result: {result.name}", result, is_result=True))
        self.draw_items(items)

    def draw_items(self, items: list[PlotItem]) -> None:
        self.figure.clear()
        if not items:
            self.figure.text(
                0.5, 0.5, "Load a signal to get started",
                ha="center", va="center", color="gray", fontsize=13,
            )
            self.canvas.draw_idle()
            return

        lo = min(i.signal.start for i in items)
        hi = max(i.signal.end for i in items)
        axes = self.figure.subplots(len(items), 1, sharex=True, squeeze=False)[:, 0]

        for ax, item in zip(axes, items):
            sig = item.signal
            color = RESULT_COLOR if item.is_result else INPUT_COLOR
            markers, stems, _ = ax.stem(sig.indices, sig.values, basefmt=" ")
            markers.set_color(color)
            markers.set_markersize(6)
            stems.set_color(color)

            ax.axhline(0, color="black", linewidth=0.8)
            ax.set_title(item.label, loc="left", fontsize=10, fontweight="bold")
            ax.set_ylabel("x(n)")
            ax.grid(True, alpha=0.3)

            y_lo, y_hi = min(sig.values.min(), 0.0), max(sig.values.max(), 0.0)
            pad = 0.15 * (y_hi - y_lo or 1.0)
            ax.set_ylim(y_lo - pad, y_hi + pad)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        axes[0].set_xlim(lo - 1, hi + 1)
        axes[-1].set_xlabel("n")
        self.canvas.draw_idle()
