from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
import logging
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class PsuSetup(QWidget):
    def __init__(self):
        super().__init__()
        self.window = QWidget()
        _layout = QHBoxLayout()
        self.window.setLayout(_layout)

        self._psuVgsbutton = PsuButtonBox("Vgs psu")
        _layout.addWidget(self._psuVgsbutton)

        _layout.addStretch()

        self.dut = QPushButton()
        self.dut.setObjectName("dut")
        self.dut.setMinimumSize(150, 150)
        #self.dut.clicked.connect(self.test)
        self.dut.setIcon(QIcon('Nmos.png'))
        self.dut.setIconSize(QtCore.QSize(130, 130))
        _layout.addWidget(self.dut)

        _layout.addStretch()

        self._psuVdsbutton = PsuButtonBox("Vds psu")
        _layout.addWidget(self._psuVdsbutton)


class PsuButtonBox(QWidget):
    def __init__(self, psuname):
        super().__init__()
        self.PsuSetupWin = None

        _layout = QVBoxLayout()
        self.button = QPushButton("+                  +\n  " + psuname
                                  + "  \n-                 -")
        stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 red, stop: 0.51 dimgrey)}"
        self.button.setStyleSheet(stylesheet)
        self.button.setMinimumSize(150, 65)
        _layout.addWidget(self.button)
        self.button.clicked.connect(self.openpsuwindow)

        self.setLayout(_layout)

    def openpsuwindow(self):
        if self.PsuSetupWin is None:
            self.PsuSetupWin = self.PsuWindow(self.parametersdictionary)
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