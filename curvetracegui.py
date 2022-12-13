import sys

import curvetracePSU
import powersupply_EMPTY
import setup
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget,
                             QPushButton, QDoubleSpinBox, QVBoxLayout, QLabel, QSpinBox)

from powersupply_EMPTY import EmptyPSU
from powersupply_KORAD import KORAD


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.VgsPSU = curvetracePSU.createPSUclass(EmptyPSU)()
        self.VdsPSU = curvetracePSU.createPSUclass(EmptyPSU)()

        self.psuVdsTestParameters = {
                                     "name": "PSU Vds",
                                     "label": object(),
                                     "PSU button": object(),
                                     "Start V": object(),
                                     "End V": object(),
                                     "Max I": object(),
                                     "Step V": object(),
                                     "Polarity": object()}

        self.psuVgsTestParameters = {
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

    def builtui(self):

        self.setWindowTitle("Curvetrace 0.2")
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
        self.PsuVgsLabel = QLabel(self.VgsPSU.name)
        self.PsuVgsLabel.setMinimumSize(110, 50)
        self.layouttopcentertopH.addWidget(self.PsuVgsLabel)

        self.layouttopcentertopH.addStretch()

        self.PsuVdsLabel = QLabel(self.VdsPSU.name)
        self.PsuVdsLabel.setMinimumSize(110, 50)
        self.layouttopcentertopH.addWidget(self.PsuVdsLabel)

    # top center top end
    # top center middle start

        self._psuVgsbutton = PsuButtonBox(self.VgsPSU, "Vds PSU")
        self.layouttopcentermiddleH.addWidget(self._psuVgsbutton)

        self.layouttopcentermiddleH.addStretch()

        self.dut = QPushButton()
        self.dut.setObjectName("dut")
        self.dut.setMinimumSize(150, 150)
        #self.dut.clicked.connect(self.test)
        self.dut.setIcon(QIcon('Nmos.png'))
        self.dut.setIconSize(QtCore.QSize(130, 130))
        self.layouttopcentermiddleH.addWidget(self.dut)

        self.layouttopcentermiddleH.addStretch()

        self._psuVdsbutton = PsuButtonBox(self.VdsPSU, "Vgs PSU")
        self.layouttopcentermiddleH.addWidget(self._psuVdsbutton)


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
        self.layouttopleftV.addWidget(self.VgsPSU.window)

# right pane start
        self.layouttoprightV.addWidget(self.VdsPSU.window)

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


class PsuButtonBox(QWidget):
    def __init__(self, psu, buttontxt):
        super().__init__()
        self.PsuSetupWin = None

        _layout = QVBoxLayout()
        self.button = QPushButton("+                  +\n  " + buttontxt
                                  + "  \n-                 -")
        stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 red, stop: 0.51 dimgrey)}"
        self.button.setStyleSheet(stylesheet)
        self.button.setMinimumSize(150, 65)
        _layout.addWidget(self.button)
        self.button.clicked.connect(lambda a: self.openpsuwindow(psu, buttontxt))

        self.setLayout(_layout)

    def openpsuwindow(self, psu, buttontxt):
        if self.PsuSetupWin is None:
            self.PsuSetupWin = setup.PsuInitWindow(psu, buttontxt)
        self.PsuSetupWin.show()

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
