import sys
import utils
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget,
                             QPushButton, QDoubleSpinBox, QVBoxLayout, QLabel, QSpinBox)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.psuVds = None  # object()
        self.psuVgs = None  # object()object()
        self.psuVdsTestParameters = {"psuobject": self.psuVds,
                                     "name": "PSU Vds",
                                     "label": object(),
                                     "PSU button": object(),
                                     "Start V": object(),
                                     "End V": object(),
                                     "Max I": object(),
                                     "Step V": object(),
                                     "Polarity": object()}

        self.psuVgsTestParameters = {"psuobject": self.psuVgs,
                                     "name": "PSU Vgs",
                                     "label": object(),
                                     "PSU button": object(),
                                     "Start V": object(),
                                     "End V": object(),
                                     "Max I": object(),
                                     "Step V": object(),
                                     "Polarity": object()}

        self.dutTestParameters = {"Idle sec": 0, "Preheat sec": 0, "Max Power": 0}

        self.builtui()

    def sanitycheck(self):
        print(self.psuVdsTestParameters)
        for key1 in self.psuVdsTestParameters:
            if key1 == "Polarity":
                print(key1, self.psuVdsTestParameters[key1]["value"],
                      self.psuVdsTestParameters[key1]["widget"].psyVgsRadioPolarity.isChecked())
            else:
                print(key1, self.psuVdsTestParameters[key1]["value"],
                      self.psuVdsTestParameters[key1]["widget"].widgetSpinbox.text())

    def test(self):
    #   print(self.psuVdsTestParameters["psuobject"].port)
        print(self.psuVgsTestParameters["psuobject"].port)

        # self.psuVdsTestParameters["psuobject"].turnon()
        # self.psuVdsTestParameters["psuobject"].setvoltage(3)
        # self.psuVdsTestParameters["psuobject"].setvoltage(0)

    def builtui(self):

        self.setWindowTitle("Curvetrace 0.1")
        self.window = QWidget()
        self.mainlayout = QVBoxLayout()

        self.layouttopH = QHBoxLayout()
        self.layouttopbottomV = QVBoxLayout()

        self.layouttopleftV = QVBoxLayout()

        self.layouttopcenterV = QVBoxLayout()

        self.layouttopcentertopH = QHBoxLayout()
        self.layouttopcentermiddleH = QHBoxLayout()
        self.layouttopcenterbottomH = QHBoxLayout()

        self.layouttoprightV = QVBoxLayout()

        self.setCentralWidget(self.window)
        self.window.setLayout(self.mainlayout)

# top center pane start
        self.PsuVgsLabel = QLabel("")
        self.PsuVgsLabel.setMinimumSize(110, 50)
        self.layouttopcentertopH.addWidget(self.PsuVgsLabel)
        self.psuVgsTestParameters["label"] = self.PsuVgsLabel

        self.layouttopcentertopH.addStretch()

        self.PsuVdsLabel = QLabel("")
        self.PsuVdsLabel.setMinimumSize(110, 50)
        self.layouttopcentertopH.addWidget(self.PsuVdsLabel)
        self.psuVdsTestParameters["label"] = self.PsuVdsLabel

    # top center top end
    # top center middle start

        self.psuVgsbutton = PsuButtonBox(self.psuVgsTestParameters)
        self.psuVgsTestParameters["PSU button"] = self.psuVgsbutton

        self.layouttopcentermiddleH.addWidget(self.psuVgsbutton)

        self.layouttopcentermiddleH.addStretch()

        self.dut = QPushButton()
        self.dut.setObjectName("dut")
        self.dut.setMinimumSize(150, 150)
        self.dut.clicked.connect(self.test)
        self.dut.setIcon(QIcon('Nmos.png'))
        self.dut.setIconSize(QtCore.QSize(130, 130))
        self.layouttopcentermiddleH.addWidget(self.dut)

        self.layouttopcentermiddleH.addStretch()

        self.psuVdsbutton = PsuButtonBox(self.psuVdsTestParameters)
        self.psuVdsTestParameters["PSU button"] = self.psuVdsbutton

        self.layouttopcentermiddleH.addWidget(self.psuVdsbutton)
    # top center middle end
    # top center bottom start
        self.IdleLabel = QLabel("Idle sec")
        self.IdleLabel.setMinimumSize(110, 50)
        self.layouttopcenterbottomH.addWidget(self.IdleLabel)

        # self.layout.addStretch()
        self.IdleSpinbox = QDoubleSpinBox()
        self.IdleSpinbox.setMinimumSize(130, 50)
        self.IdleSpinbox.setMaximumSize(130, 50)
        self.IdleSpinbox.setMinimum(0)
        self.IdleSpinbox.setMaximum(10)
        self.IdleSpinbox.setSingleStep(0.01)

        self.layouttopcenterbottomH.addWidget(self.IdleSpinbox)

        self.layouttopcenterbottomH.addStretch()

        self.PheatLabel = QLabel("Preheat sec")
        self.PheatLabel.setMinimumSize(160, 50)
        self.layouttopcenterbottomH.addWidget(self.PheatLabel)

        # self.layout.addStretch()
        self.PheatSpinbox = QSpinBox()
        self.PheatSpinbox.setMinimumSize(130, 50)
        self.PheatSpinbox.setMaximumSize(130, 50)
        self.PheatSpinbox.setMinimum(0)
        self.PheatSpinbox.setMaximum(100)
        self.layouttopcenterbottomH.addWidget(self.PheatSpinbox)

        self.layouttopcenterbottomH.addStretch()

        self.MaxpwrLabel = QLabel("Max Power")
        self.MaxpwrLabel.setMinimumSize(150, 50)
        self.layouttopcenterbottomH.addWidget(self.MaxpwrLabel)

        # self.layout.addStretch()
        self.MaxpwrSpinbox = QSpinBox()
        self.MaxpwrSpinbox.setMinimumSize(130, 50)
        self.MaxpwrSpinbox.setMaximumSize(130, 50)
        self.MaxpwrSpinbox.setMinimum(0)
        self.MaxpwrSpinbox.setMaximum(100)
        self.layouttopcenterbottomH.addWidget(self.MaxpwrSpinbox)
    # top center bottom end

# top center pane end

# top left pane start
        self.psyVgsTestParametersPane = ParametersPaneWidget(self.psuVgsTestParameters)
        self.layouttopleftV.addWidget(self.psyVgsTestParametersPane)

# right pane start
        self.psyVdsTestParametersPane = ParametersPaneWidget(self.psuVdsTestParameters)
        self.layouttoprightV.addWidget(self.psyVdsTestParametersPane)

# right pane end

        self.layouttopH.addLayout(self.layouttopleftV)
        self.layouttopH.addStretch()

        self.layouttopcenterV.addStretch()
        self.layouttopcenterV.addLayout(self.layouttopcentertopH)
        self.layouttopcentermiddleH.addStretch()
        self.layouttopcenterV.addLayout(self.layouttopcentermiddleH)
        self.layouttopcentermiddleH.addStretch()
        self.layouttopcenterV.addLayout(self.layouttopcenterbottomH)
        self.layouttopcenterV.addStretch()

        self.layouttopH.addLayout(self.layouttopcenterV)
        self.layouttopH.addStretch()

        self.layouttopH.addLayout(self.layouttoprightV)

        self.mainlayout.addLayout(self.layouttopH)
        self.mainlayout.addStretch()
        self.mainlayout.addLayout(self.layouttopbottomV)
        self.mainlayout.addStretch()


class ParametersPaneWidget(QWidget):
    def __init__(self, parametersdictionary):
        super().__init__()
        self.parameter = parametersdictionary

        self.PaneLayout = QVBoxLayout()
        for p in parametersdictionary.keys():
            if p not in ("Polarity", "name", "psuobject", "label", "PSU button"):
                parametersdictionary[p] = ParameterWidget(p)
                self.PaneLayout.addWidget(parametersdictionary[p])
                self.PaneLayout.addStretch()
        self.setLayout(self.PaneLayout)


class ParameterWidget(QWidget):
    def __init__(self, parameter):
        super().__init__()
        self.parameter = parameter

        self.layout = QHBoxLayout()

        self.widgetLabel = QLabel(parameter)
        self.widgetLabel.setMinimumSize(110, 50)
        self.layout.addWidget(self.widgetLabel)

        self.widgetSpinbox = QDoubleSpinBox()
        self.widgetSpinbox.setMinimumSize(130, 50)
        self.widgetSpinbox.setMaximumSize(130, 50)
        self.widgetSpinbox.setMinimum(0)
        self.widgetSpinbox.setMaximum(100)
        self.widgetSpinbox.setSingleStep(0.01)
        self.layout.addWidget(self.widgetSpinbox)

        self.setLayout(self.layout)


class PsuButtonBox(QWidget):
    def __init__(self, parametersdictionary):
        super().__init__()
        self.PsuSetupWin = None
        self.parametersdictionary = parametersdictionary

        self.layout = QVBoxLayout()
        self.button = QPushButton("+                  +\n  " + self.parametersdictionary["name"]
                                  + "  \n-                 -")
        stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 red, stop: 0.51 dimgrey)}"
        self.button.setStyleSheet(stylesheet)
        self.button.setMinimumSize(150, 65)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.openpsuwindow)

        self.setLayout(self.layout)

    def openpsuwindow(self):
        if self.PsuSetupWin is None:
            self.PsuSetupWin = utils.PsuWindow(self.parametersdictionary)
        self.PsuSetupWin.show()
        # else:
        #     self.PsuSetupWin.close()  # Close window.
        #     self.PsuSetupWin = None  # Discard reference.

    def set(self, value):
        self.dictionaryvalue = value
        if value:
            stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 red, stop: 0.51 dimgrey)}"
            self.button.setStyleSheet(stylesheet)
            self.button.setText('+                  +\n  PSU Vgs  \n-                 -')
        else:
            stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 dimgrey, stop: 0.51 red)}"
            self.button.setStyleSheet(stylesheet)
            self.button.setText('-                  -\n  PSU Vgs  \n+                 +')


app = QApplication(sys.argv)
window = MainWindow()
window.show()
exit(app.exec_())
