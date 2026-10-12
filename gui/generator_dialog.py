from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QComboBox,
    QDoubleSpinBox,
    QDialogButtonBox,
    QVBoxLayout,
    QLineEdit,
)


class GeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Signal Generation")
        self.setMinimumWidth(350)

        # Wave type
        self.type_input = QComboBox()
        self.type_input.addItems(["sine", "cosine"])

        # Amplitude
        self.amplitude_input = QDoubleSpinBox()
        self.amplitude_input.setRange(0.0, 10000.0)
        self.amplitude_input.setValue(1.0)
        self.amplitude_input.setSingleStep(0.5)

        # Phase (theta), in radians
        self.theta_input = QDoubleSpinBox()
        self.theta_input.setRange(-1000.0, 1000.0)
        self.theta_input.setValue(0.0)
        self.theta_input.setSingleStep(0.1)
        self.theta_input.setDecimals(4)

        # Analog frequency (f)
        self.f_input = QDoubleSpinBox()
        self.f_input.setRange(0.01, 10000.0)
        self.f_input.setValue(1.0)
        self.f_input.setSingleStep(0.5)

        # Sampling frequency (FS)
        self.FS_input = QDoubleSpinBox()
        self.FS_input.setRange(0.01, 100000.0)
        self.FS_input.setValue(10.0)
        self.FS_input.setSingleStep(1.0)

        # Duration in seconds
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0.01, 10000.0)
        self.duration_input.setValue(1.0)
        self.duration_input.setSingleStep(0.5)

        # Optional signal name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. My Sine Wave")

        # Arrange input fields
        form = QFormLayout()
        form.addRow("Wave Type:", self.type_input)
        form.addRow("Amplitude (A):", self.amplitude_input)
        form.addRow("Phase (theta, radians):", self.theta_input)
        form.addRow("Frequency (f, Hz):", self.f_input)
        form.addRow("Sampling Frequency (FS, Hz):", self.FS_input)
       # form.addRow("Duration (seconds):", self.duration_input)
        form.addRow("Signal Name (optional):", self.name_input)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_parameters(self):
        return {
            "Type": self.type_input.currentText(),
            "amplitude": self.amplitude_input.value(),
            "theta": self.theta_input.value(),
            "f": self.f_input.value(),
            "FS": self.FS_input.value(),
           # "duration": self.duration_input.value(),
            "name": self.name_input.text().strip() or None,
        }
