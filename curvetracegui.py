import sys
from PyQt5.QtCore import pyqtSignal, QThread
from plot import plotwin
from setup import PsuInitWindow
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget,
                             QPushButton, QDoubleSpinBox, QVBoxLayout, QLabel, QSpinBox, QFrame,
                             QSizePolicy, QCheckBox, QMenu, QAction, QMessageBox)
import traceroutine
from powersupply_EMPTY import EmptyPSU
from VirtualPSU import VirtualPSU


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.PSUdict = {"Vgs PSU": VirtualPSU([EmptyPSU()]),
                        "Vds PSU": VirtualPSU([EmptyPSU()])}

        self.PsuSetupWin = PsuInitWindow(self.PSUdict)
        self.PsuSetupWin.Vgspolaritychanged.connect(lambda s: self.psuVgsbutton.set(s))
        self.PsuSetupWin.Vdspolaritychanged.connect(lambda s: self.psuVdsbutton.set(s))
        self.PsuSetupWin.updateMainWindow.connect(self.buildui)

        self.dutTestParameters = {"Idle sec": 0, "Preheat sec": 0, "Max Power": 0}
        self.data = None

        self.buildui()

        self.menuBar = self.menuBar()
        file_menu = QMenu("&File", self)
        self.menuBar.addMenu(file_menu)

        self._savesettingsMenuItem = QAction(QIcon(), '&Save startup Settings', self)
        self._savesettingsMenuItem.setStatusTip('New document')
        self._savesettingsMenuItem.triggered.connect(self.PsuSetupWin.savesettings)

        file_menu.addAction(self._savesettingsMenuItem)

        self._testMenuItem = QAction(QIcon(), '&Test  ', self)
        self._testMenuItem.setStatusTip('Test')
        self._testMenuItem.triggered.connect(self.test2)

        file_menu.addAction(self._testMenuItem)

        self.PsuSetupWin.applysettings()

    def buildui(self):

        self.window = QWidget()
        self.setCentralWidget(self.window)
        self.mainlayout = QVBoxLayout()
        self.window.setLayout(self.mainlayout)
        self.setWindowTitle("Curvetrace 0.3")

        self.layouttopH = QHBoxLayout()
        self.layoutbottomV = QVBoxLayout()

        self.layouttopleftV = QVBoxLayout()

        self.layouttopcenterV = QVBoxLayout()

        self.layouttopcentertopH = QHBoxLayout()
        self.layouttopcentermiddleH = QHBoxLayout()
        self.layouttopcenterbottomH = QHBoxLayout()

        self.layouttoprightV = QVBoxLayout()

        self.layoutbottomH = QHBoxLayout()

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
        self.psuVgsbutton.PsuButtonPressed.connect(lambda x: self.openpsuwindow())

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
        self.psuVdsbutton.PsuButtonPressed.connect(lambda x: self.openpsuwindow())

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
        self.MaxpwrSpinbox.setMaximum(300)
        self.layouttopcenterbottomH.addWidget(self.MaxpwrSpinbox)
        # top center bottom end

        # top center pane end

        # top left pane start
        self.layouttopleftV.addWidget(self.PSUdict["Vgs PSU"].PSUwindow)

        # right pane start
        self.layouttoprightV.addWidget(self.PSUdict["Vds PSU"].PSUwindow)

        # right pane end
        # bottom start

        self.plot_area = plotwin()
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator.setLineWidth(3)

        self.layoutbottomV.addWidget(separator)

        self.smoothcurveCheckB = QCheckBox("Smooth Curves")
        self.smoothcurveCheckB.toggled.connect(lambda x: self.plot_area.smoothcurves(self.data, x))
        self.layoutbottomH.addWidget(self.smoothcurveCheckB)

        self.plotlimitsCheckB = QCheckBox("Plot Power lim")
        self.plotlimitsCheckB.toggled.connect(lambda x: self.plot_area.plotlimits(self.MaxpwrSpinbox.value(),
                                                                                  self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.value(),
                                                                                  self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.value(),
                                                                                  x))
        self.layoutbottomH.addWidget(self.plotlimitsCheckB)

        self.savecurvesB = QPushButton("Save")
        self.savecurvesB.setMinimumSize(130, 50)
        self.savecurvesB.setMaximumSize(130, 50)
        self.savecurvesB.pressed.connect(self.savecurves)
        self.layoutbottomH.addWidget(self.savecurvesB)

        self.layoutbottomV.addLayout(self.layoutbottomH)

        self.layoutbottomV.addWidget(self.plot_area)

        # bottom end

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

        self.mainlayout.addLayout(self.layoutbottomV)
        self.mainlayout.addStretch()

    def savecurves(self):
        print("pressed")

    def openpsuwindow(self):
        self.PsuSetupWin.show()

    def test(self):
        self.starttracing()

    def test2(self):
        self.PsuSetupWin._settings.clear()
        print(self.PsuSetupWin)
        if self.PsuSetupWin:
            print("is open psu setup win")

    def starttracing(self):
        print()
        if self.PSUdict["Vds PSU"].name != "Empty PSU":
            self.freeze(True)
            self.plot_area.reset()
            self.thread = QThread()
            self.worker = traceroutine.worker(self.PSUdict, self.MaxpwrSpinbox)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.traceroutine)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.finished.connect(self.getdata)
            self.worker.finished.connect(lambda x: self.freeze(False))
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.newcurve.connect(lambda x: self.plot_area.newcurve(x))
            self.worker.plotdata.connect(lambda x: self.plot_area.plotdata(x))

            self.thread.start()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("No PSU for Vds has been setup")
            msg.setInformativeText("Press on one of the PSU buttons - red/gray buttons- to setup the PSU")
            msg.setWindowTitle("Vds missing")
            msg.setDetailedText("In the case that only 1 PSU will be used, it must be the Vds PSU not the Vgs")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def getdata(self, data):
        self.data = data

    def freeze(self, freeze):
        self.psuVgsbutton.button.setDisabled(freeze)
        self.psuVdsbutton.button.setDisabled(freeze)
        self.PSUdict["Vgs PSU"].disablespinbxs(freeze)
        self.PSUdict["Vds PSU"].disablespinbxs(freeze)
        self.IdleSpinbox.setDisabled(freeze)
        self.PheatLabel.setDisabled(freeze)
        self.MaxpwrLabel.setDisabled(freeze)
        self.smoothcurveCheckB.setDisabled(freeze)
        self.plotlimitsCheckB.setDisabled(freeze)
        self.savecurvesB.setDisabled(freeze)

    def closeEvent(self, event):
        if self.PsuSetupWin:
            self.PsuSetupWin.deleteLater()


class PsuButtonBox(QWidget):
    PsuButtonPressed = pyqtSignal(str)

    def __init__(self, psu_dict, psu_key):
        super().__init__()
        self.psuKey = psu_key
        _layout = QVBoxLayout()
        self.button = QPushButton()
        self.set(psu_dict[psu_key].polarity)
        self.button.setMinimumSize(150, 65)
        _layout.addWidget(self.button)
        self.button.clicked.connect(lambda a: self.PsuButtonPressed.emit(psu_key))
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
