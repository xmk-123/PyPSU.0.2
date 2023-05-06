import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QSpinBox, QPushButton, QApplication, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QDialogButtonBox, QDoubleSpinBox


class ParametersDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Parameters")

        self.formGroupBox = QGroupBox("")
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addStretch()
        LayoutH = QHBoxLayout()
        _submit_button = QPushButton("Submit")
        _cancel_button = QPushButton("Cancel")
        LayoutH.addWidget(_submit_button)
        LayoutH.addWidget(_cancel_button)
        _submit_button.pressed.connect(self.save_parameters)
        _cancel_button.pressed.connect(self.close)

        mainLayout.addLayout(LayoutH)

        self.setLayout(mainLayout)

        self.heater_resistance = QSpinBox()
        self.heater_max_power = QSpinBox()
        self.heater_max_power.setMaximum(300)
        self.shutdown_temperature = QSpinBox()
        self.temperature_allowance = QDoubleSpinBox()
        self.temperature_matches_for_stable = QSpinBox()

        form = QFormLayout()
        self.formGroupBox.setLayout(form)

        form.addRow(QLabel("Heater resistance"), self.heater_resistance)
        form.addRow(QLabel("heater max_power"), self.heater_max_power)
        form.addRow(QLabel("shutdown temperature"), self.shutdown_temperature)
        form.addRow(QLabel("temperature allowance"), self.temperature_allowance)
        form.addRow(QLabel("temperature matches_for_stable"), self.temperature_matches_for_stable)

        self.saved_parameters = QSettings()
        self.load_parameters()

    def save_parameters(self):
        self.saved_parameters.setValue("heater_resistance",  self.heater_resistance.value())
        self.saved_parameters.setValue("heater_max_power", self.heater_max_power.value())
        self.saved_parameters.setValue("shutdown_temperature", self.shutdown_temperature.value())
        self.saved_parameters.setValue("temperature_allowance", self.temperature_allowance.value())
        self.saved_parameters.setValue("temperature_matches_for_stable", self.temperature_matches_for_stable.value())
        self.done(1)

    def load_parameters(self):
        self.heater_resistance.setValue(int(self.saved_parameters.value("heater_resistance")))
        self.heater_max_power.setValue(int(self.saved_parameters.value("heater_max_power")))
        self.shutdown_temperature.setValue(int(self.saved_parameters.value("shutdown_temperature")))
        self.temperature_allowance.setValue(float(self.saved_parameters.value("temperature_allowance")))
        self.temperature_matches_for_stable.setValue(int(self.saved_parameters.value("temperature_matches_for_stable")))


