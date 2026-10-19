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
QUANTIZATION_COLORS = {
    "original": "#315f63",
    "quantized": "#59249a",
    "error": "#777943",
}
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

    @staticmethod
    def _style_axes(ax, signals, zero_color: str = "black", zero_linestyle: str = "-") -> None:
        """Zero line, grid, integer n ticks and y-limits that fit every signal."""
        ax.axhline(0, color=zero_color, linewidth=0.8, linestyle=zero_linestyle)
        ax.set_ylabel("x(n)")
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        y_lo = min((float(s.values.min()) for s in signals), default=0.0)
        y_hi = max((float(s.values.max()) for s in signals), default=0.0)
        y_lo = min(y_lo, 0.0)
        y_hi = max(y_hi, 0.0)
        pad = 0.15 * (y_hi - y_lo or 1.0)
        ax.set_ylim(y_lo - pad, y_hi + pad)

    def show_quantization(
        self,
        original,
        quantized,
        error,
        mode: str = "discrete",
        *,
        show_original: bool = True,
        show_quantized: bool = True,
        show_error: bool = True,
    ) -> None:
        """Overlay the source signal, quantized staircase, and quantization error."""
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, got '{mode}'")

        self.figure.clear()
        ax = self.figure.subplots()
        visible_signals = []

        if show_original:
            self._draw_signal(
                ax, original, QUANTIZATION_COLORS["original"], mode, "Original analog signal"
            )
            visible_signals.append(original)
        if show_quantized:
            if mode == "continuous":
                ax.step(
                    quantized.indices,
                    quantized.values,
                    where="mid",
                    color=QUANTIZATION_COLORS["quantized"],
                    linewidth=2,
                    label="Quantized digital signal",
                )
            else:
                self._draw_signal(
                    ax, quantized, QUANTIZATION_COLORS["quantized"], mode,
                    "Quantized digital signal",
                )
            visible_signals.append(quantized)
        if show_error:
            self._draw_signal(
                ax, error, QUANTIZATION_COLORS["error"], mode, "Quantization error signal"
            )
            visible_signals.append(error)

        self._style_axes(
            ax, visible_signals, zero_color="#762d2d", zero_linestyle="--"
        )
        if visible_signals:
            ax.legend(loc="upper right")
        ax.set_title("Quantization", loc="left", fontsize=12, fontweight="bold")
        ax.set_ylabel("Amplitude")
        ax.set_xlabel("Time (sample index)")
        ax.set_xlim(original.start - 1, original.end + 1)
        self.canvas.draw_idle()

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

            self._style_axes(ax, [i.signal for i in group])
            if overlay:
                ax.legend(loc="upper right")
            else:
                ax.set_title(group[0].label, loc="left", fontsize=10, fontweight="bold")

        all_axes = [ax for ax, _ in groups]
        all_axes[0].set_xlim(lo - 1, hi + 1)
        all_axes[-1].set_xlabel("n")
        self.canvas.draw_idle()