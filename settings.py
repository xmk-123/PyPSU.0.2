import sys

from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QSpinBox, QPushButton, QApplication, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QDialogButtonBox


class SettingsDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")

        self.formGroupBox = QGroupBox("")
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addStretch()
        LayoutH = QHBoxLayout()
        LayoutH.addWidget(QPushButton("Submit"))

        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        button = buttonBox.button(QDialogButtonBox.Apply)
        button.clicked.connect(self.apply_settings)
        buttonBox.rejected.connect(self.reject)

        # mainLayout.addLayout(LayoutH)

        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)

        self.heater_resistance = QSpinBox()
        self.heater_max_power = QSpinBox()
        self.shutdown_temperature = QSpinBox()
        self.temperature_allowance = QSpinBox()
        self.temperature_matches_for_stable = QSpinBox()

        form = QFormLayout()
        self.formGroupBox.setLayout(form)

        form.addRow(QLabel("Heater resistance"), self.heater_resistance)
        form.addRow(QLabel("heater max_power"), self.heater_max_power)
        form.addRow(QLabel("shutdown temperature"), self.shutdown_temperature)
        form.addRow(QLabel("temperature allowance"), self.temperature_allowance)
        form.addRow(QLabel("temperature matches_for_stable"), self.temperature_matches_for_stable)

    def apply_settings(self):
        print("accepted")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    sys.exit(dialog.exec_())

