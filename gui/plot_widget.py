from __future__ import annotations
from dataclasses import dataclass
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PySide6.QtWidgets import QVBoxLayout, QWidget
from dsp.discrete_signal import DiscreteSignal

INPUT_COLOR = "#1f77b4"
RESULT_COLOR = "#d62728"
OVERLAY_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
MODES = ("discrete", "continuous")


@dataclass
class PlotItem:
    label: str
    signal: DiscreteSignal
    is_result: bool = False


class SignalToolbar(NavigationToolbar2QT):
    toolitems = [
        item for item in NavigationToolbar2QT.toolitems
        if item[0] in ("Back", "Forward", "Pan", "Zoom", "Save")
    ]


class SignalPlot(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.figure = Figure(layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = SignalToolbar(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)
        self.clear()

    def clear(self) -> None:
        self.draw_items([])

    def show_signals(self, signals, mode: str = "discrete", overlay: bool = False) -> None:
        self.draw_items([PlotItem(s.name, s) for s in signals], mode, overlay)

    def show_operation(self, inputs, result: DiscreteSignal) -> None:
        items = [PlotItem(f"Input: {s.name}", s) for s in inputs]
        items.append(PlotItem(f"Result: {result.name}", result, is_result=True))
        self.draw_items(items)

    @staticmethod
    def _draw_signal(ax, sig: DiscreteSignal, color: str, mode: str, label: str) -> None:
        if mode == "continuous":
            ax.plot(sig.indices, sig.values, color=color, linewidth=1.8, label=label)
        else:
            markers, stems, _ = ax.stem(sig.indices, sig.values, basefmt=" ", label=label)
            markers.set_color(color)
            markers.set_markersize(6)
            stems.set_color(color)

    def draw_items(self, items: list[PlotItem], mode: str = "discrete", overlay: bool = False) -> None:
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, got '{mode}'")

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

        # Each group is (axes, items drawn on it): one shared axes, or one per signal.
        if overlay:
            groups = [(self.figure.subplots(), items)]
        else:
            axes = self.figure.subplots(len(items), 1, sharex=True, squeeze=False)[:, 0]
            groups = [(ax, [item]) for ax, item in zip(axes, items)]

        for ax, group in groups:
            for k, item in enumerate(group):
                if item.is_result:
                    color = RESULT_COLOR
                elif overlay:
                    color = OVERLAY_COLORS[k % len(OVERLAY_COLORS)]
                else:
                    color = INPUT_COLOR
                self._draw_signal(ax, item.signal, color, mode, item.label)

            ax.axhline(0, color="black", linewidth=0.8)
            ax.set_ylabel("x(n)")
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            if overlay:
                ax.legend(loc="upper right")
            else:
                ax.set_title(group[0].label, loc="left", fontsize=10, fontweight="bold")

            y_lo = min(min(i.signal.values.min() for i in group), 0.0)
            y_hi = max(max(i.signal.values.max() for i in group), 0.0)
            pad = 0.15 * (y_hi - y_lo or 1.0)
            ax.set_ylim(y_lo - pad, y_hi + pad)

        all_axes = [ax for ax, _ in groups]
        all_axes[0].set_xlim(lo - 1, hi + 1)
        all_axes[-1].set_xlabel("n")
        self.canvas.draw_idle()