from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PySide6.QtWidgets import QVBoxLayout, QWidget
from dsp.discrete_signal import ContinuousWave, DiscreteSignal

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
    def _continuous_samples(
        wave: ContinuousWave,
    ) -> tuple[np.ndarray, np.ndarray]:
        sample_count = max(
            1000,
            int(np.ceil(wave.duration * wave.frequency * 100)) + 1,
        )
        times = np.linspace(0, wave.duration, sample_count)
        return times, wave.values_at(times)

    @staticmethod
    def _draw_signal(
        ax,
        sig: DiscreteSignal,
        color: str,
        mode: str,
        label: str,
        analytic_continuous: bool,
    ) -> np.ndarray:
        if mode == "continuous":
            if analytic_continuous:
                times, values = SignalPlot._continuous_samples(sig.continuous_wave)
                ax.plot(times, values, color=color, linewidth=1.8, label=label)
                return values
            ax.plot(sig.indices, sig.values, color=color, linewidth=1.8, label=label)
        else:
            markers, stems, _ = ax.stem(sig.indices, sig.values, basefmt=" ", label=label)
            markers.set_color(color)
            markers.set_markersize(6)
            stems.set_color(color)
        return sig.values

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

        analytic_continuous = mode == "continuous" and all(
            item.signal.continuous_wave is not None for item in items
        )
        if analytic_continuous:
            x_lo = 0.0
            x_hi = max(item.signal.continuous_wave.duration for item in items)
        else:
            x_lo = min(i.signal.start for i in items) - 1
            x_hi = max(i.signal.end for i in items) + 1

        # Each group is (axes, items drawn on it): one shared axes, or one per signal.
        if overlay:
            groups = [(self.figure.subplots(), items)]
        else:
            axes = self.figure.subplots(len(items), 1, sharex=True, squeeze=False)[:, 0]
            groups = [(ax, [item]) for ax, item in zip(axes, items)]

        for ax, group in groups:
            plotted_values = []
            for k, item in enumerate(group):
                if item.is_result:
                    color = RESULT_COLOR
                elif overlay:
                    color = OVERLAY_COLORS[k % len(OVERLAY_COLORS)]
                else:
                    color = INPUT_COLOR
                plotted_values.append(
                    self._draw_signal(
                        ax,
                        item.signal,
                        color,
                        mode,
                        item.label,
                        analytic_continuous,
                    )
                )

            ax.axhline(0, color="black", linewidth=0.8)
            ax.set_ylabel("Amplitude" if analytic_continuous else "x(n)")
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_locator(MaxNLocator(integer=not analytic_continuous))
            if overlay:
                ax.legend(loc="upper right")
            else:
                ax.set_title(group[0].label, loc="left", fontsize=10, fontweight="bold")

            y_lo = min(min(values.min() for values in plotted_values), 0.0)
            y_hi = max(max(values.max() for values in plotted_values), 0.0)
            pad = 0.15 * (y_hi - y_lo or 1.0)
            ax.set_ylim(y_lo - pad, y_hi + pad)

        all_axes = [ax for ax, _ in groups]
        all_axes[0].set_xlim(x_lo, x_hi)
        all_axes[-1].set_xlabel("Time (s)" if analytic_continuous else "n")
        self.canvas.draw_idle()
