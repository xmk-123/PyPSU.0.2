import sys

import curvetracePSU
import powersupply_EMPTY
import setup
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget,
                             QPushButton, QDoubleSpinBox, QVBoxLayout, QLabel, QSpinBox)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.VgsPSU = curvetracePSU.CurvetracePSU(powersupply_EMPTY.EmptyPSU(), "Vgs PSU")
        self.VdsPSU = curvetracePSU.CurvetracePSU(powersupply_EMPTY.EmptyPSU(), "Vds PSU")
        # self.VgsPSU = curvetracePSU.CurvetracePSU(powersupply_KORAD.KORAD(), "Vgs PSU")
        # self.VdsPSU = curvetracePSU.CurvetracePSU("Vds PSU")

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

        self.Vgspsusetup = setup.PsuSetup()
        self.layouttopcentermiddleH.addWidget(self.Vgspsusetup.window)


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


app = QApplication(sys.argv)
window = MainWindow()
window.show()
exit(app.exec_())
