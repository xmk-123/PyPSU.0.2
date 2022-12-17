import sys
import time
from PyQt5.QtCore import pyqtSignal
import curvetracePSU
import setup
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget,
                             QPushButton, QDoubleSpinBox, QVBoxLayout, QLabel, QSpinBox)
from powersupply_EMPTY import EmptyPSU


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.PSUdict = {"Vgs PSU": curvetracePSU.createPSUclass(EmptyPSU)(),
                        "Vds PSU": curvetracePSU.createPSUclass(EmptyPSU)()}
        self.dutTestParameters = {"Idle sec": 0, "Preheat sec": 0, "Max Power": 0}

        self.PsuSetupWin = None
        self.builtui()

    def builtui(self):

        self.setWindowTitle("Curvetrace 0.3")
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
        self.PsuVgsLabel = QLabel(self.PSUdict["Vgs PSU"].name)
        self.PsuVgsLabel.setMinimumSize(110, 50)
        self.layouttopcentertopH.addWidget(self.PsuVgsLabel)

        self.layouttopcentertopH.addStretch()

        self.PsuVdsLabel = QLabel(self.PSUdict["Vds PSU"].name)
        self.PsuVdsLabel.setMinimumSize(110, 50)
        self.layouttopcentertopH.addWidget(self.PsuVdsLabel)

    # top center top end
    # top center middle start

        self.psuVgsbutton = PsuButtonBox(self.PSUdict, "Vgs PSU")
        self.layouttopcentermiddleH.addWidget(self.psuVgsbutton)
        self.psuVgsbutton.PsuButtonPressed.connect(lambda x: self.openpsuwindow(self.PSUdict))

        self.layouttopcentermiddleH.addStretch()

        self.dut = QPushButton()
        self.dut.setObjectName("dut")
        self.dut.setMinimumSize(150, 150)
        self.dut.clicked.connect(self.test)
        self.dut.setIcon(QIcon('Nmos.png'))
        self.dut.setIconSize(QtCore.QSize(130, 130))
        self.layouttopcentermiddleH.addWidget(self.dut)

        self.layouttopcentermiddleH.addStretch()

        self.psuVdsbutton = PsuButtonBox(self.PSUdict, "Vds PSU")
        self.layouttopcentermiddleH.addWidget(self.psuVdsbutton)
        self.psuVdsbutton.PsuButtonPressed.connect(lambda x: self.openpsuwindow(self.PSUdict))

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
        self.layouttopleftV.addWidget(self.PSUdict["Vgs PSU"].window)

# right pane start
        self.layouttoprightV.addWidget(self.PSUdict["Vds PSU"].window)

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

    def openpsuwindow(self, PSUdict):
        if self.PsuSetupWin is None:
            self.PsuSetupWin = setup.PsuInitWindow(PSUdict)
            # self.PsuSetupWin.setWindowModality(QtCore.Qt.WindowModal)
            self.PsuSetupWin.Vgspolaritychanged.connect(lambda s: self.psuVgsbutton.set(s))
            self.PsuSetupWin.Vdspolaritychanged.connect(lambda s: self.psuVdsbutton.set(s))
            self.PsuSetupWin.updateMainWindow.connect(self.builtui)
        self.PsuSetupWin.show()

    def test(self):
        self.PSUdict["Vgs PSU"].turnon()
        self.PSUdict["Vgs PSU"].setvoltage(3)
        time.sleep(5)
        self.PSUdict["Vgs PSU"].setvoltage(0)
        self.PSUdict["Vgs PSU"].turnoff()

        # self.psuVgsbutton.PsuSetupWin.show()
        # print(get_referrers(self.psuVgsbutton.PsuSetupWin))
        # b = get_referrers(self.PSUdict)
        # for i in get_referrers(self.PSUdict):
        #     print(i)
        # print(getrefcount(self.PSUdict)) # print(self.PSUdict["Vds PSU"].name)


class PsuButtonBox(QWidget):
    PsuButtonPressed = pyqtSignal(str)

    def __init__(self, PSUdict, psuKey):
        super().__init__()
        self.psuKey = psuKey
        _layout = QVBoxLayout()
        self.button = QPushButton()
        self.set(PSUdict[psuKey].polarity)
        self.button.setMinimumSize(150, 65)
        _layout.addWidget(self.button)
        self.button.clicked.connect(lambda a: self.PsuButtonPressed.emit(psuKey))
        self.setLayout(_layout)

    def set(self, value):
        if value:
            stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 red, stop: 0.51 dimgrey)}"
            self.button.setStyleSheet(stylesheet)
            self.button.setText("+                  +\n" + self.psuKey + "\n-                 -")
        else:
            stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 dimgrey, stop: 0.51 red)}"
            self.button.setStyleSheet(stylesheet)
            self.button.setText("-                  -\n" + self.psuKey + "\n+                 +")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
exit(app.exec_())
