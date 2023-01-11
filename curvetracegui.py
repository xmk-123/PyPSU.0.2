import sys
import time

from PyQt5.QtCore import pyqtSignal, QThread
from plot import PlotWin
from setup import PsuInitWindow
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget,
                             QPushButton, QVBoxLayout, QLabel, QSpinBox, QFrame,
                             QSizePolicy, QCheckBox, QMenu, QAction, QMessageBox)
import traceroutine
from powersupply_EMPTY import EmptyPSU
from VirtualPSU import VirtualPSU
import temperaturemonitor


class MainWindow(QMainWindow):

    stop_temperature_sensor = pyqtSignal()

    def __init__(self):
        super().__init__()
        # self.showMaximized()
        self.PSUdict = {"Vgs PSU": VirtualPSU([EmptyPSU()]),
                        "Vds PSU": VirtualPSU([EmptyPSU()])}
        self.temperature_stable = {"status": False}

        self.PsuSetupWin = PsuInitWindow(self.PSUdict)
        self.PsuSetupWin.Vgspolaritychanged.connect(lambda s: self.psuVgsbutton.set(s))
        self.PsuSetupWin.Vdspolaritychanged.connect(lambda s: self.psuVdsbutton.set(s))
        self.PsuSetupWin.updateMainWindow.connect(self.buildui)

        # self.dutTestParameters = {"Idle sec": 0, "Preheat sec": 0, "Max Power": 0}
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

        self.layouttopcenterV = QVBoxLayout()

        self.layouttopcentertopH = QHBoxLayout()
        self.layouttopcentermiddleH = QHBoxLayout()
        self.layouttopcenterbottomH = QHBoxLayout()

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
        self.dut_widgets = DutSet()
        self.layouttopcenterbottomH.addWidget(self.dut_widgets)
        self.PSUdict["DUT settings"] = self.dut_widgets
        # top center bottom end
    # top center pane end

    # bottom start
        self.plot_area = PlotWin()
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator.setLineWidth(3)

        self.layoutbottomV.addWidget(separator)

        self.smoothcurveCheckB = QCheckBox("Smooth Curves")
        self.smoothcurveCheckB.toggled.connect(lambda x: self.plot_area.smoothcurves(self.data, x))
        self.layoutbottomH.addWidget(self.smoothcurveCheckB)

        self.plotlimitsCheckB = QCheckBox("Plot Power lim")
        self.plotlimitsCheckB.toggled.connect(lambda x: self.plot_area.plotlimits(self.DUTMaxPSpinbox.value(),
                                                                                  self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.value(),
                                                                                  self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.value(),
                                                                                  x))
        self.layoutbottomH.addWidget(self.plotlimitsCheckB)

        self.savecurvesB = QPushButton("Save")
        self.savecurvesB.setMinimumSize(130, 50)
        self.savecurvesB.setMaximumSize(130, 50)
        self.savecurvesB.pressed.connect(self.savecurves)
        self.layoutbottomH.addWidget(self.savecurvesB)
    # bottom end

        self.layouttopH.addWidget(self.PSUdict["Vgs PSU"].PSUwindow)
        self.layouttopH.addStretch()

        self.layouttopcenterV.addLayout(self.layouttopcentertopH)
        self.layouttopcenterV.addLayout(self.layouttopcentermiddleH)
        self.layouttopcenterV.addLayout(self.layouttopcenterbottomH)

        self.layouttopH.addLayout(self.layouttopcenterV, 0)

        self.layouttopH.addStretch()
        self.layouttopH.addWidget(self.PSUdict["Vds PSU"].PSUwindow)

        self.mainlayout.addLayout(self.layouttopH, 0)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        # separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator.setLineWidth(3)

        self.mainlayout.addWidget(separator)
        self.mainlayout.addLayout(self.layoutbottomH)
        self.mainlayout.addWidget(self.plot_area)

    def savecurves(self):
        print("pressed")

    def openpsuwindow(self):
        self.PsuSetupWin.show()

    def test(self):
        self.start_temperature_sensor()
        self.starttracing()

    def test2(self):
        try:
            print("tracing thread " + str(self.tracing_thread.isRunning()))
        except BaseException as e:
            print(e)
        try:
            print("temperature thread " + str(self.temperature_thread.isRunning()))
        except BaseException as e:
            print(e)


        # self.PsuSetupWin._settings.clear()
        # print(self.PsuSetupWin)
        # if self.PsuSetupWin:
        #     print("is open psu setup win")

    def starttracing(self):
        if self.PSUdict["Vds PSU"].name != "Empty PSU":
            self.freeze(True)
            self.plot_area.reset()

            self.tracing_thread = QThread()
            self.tracing_worker = traceroutine.Worker(self.PSUdict, self.temperature_stable)
            self.tracing_worker.moveToThread(self.tracing_thread)

            self.tracing_thread.started.connect(self.tracing_worker.traceroutine)
            self.tracing_thread.finished.connect(self.tracing_thread.deleteLater)
            self.tracing_worker.finished.connect(self.getdata)
            self.tracing_worker.finished.connect(lambda x: self.freeze(False))
            self.tracing_worker.finished.connect(self.tracing_thread.quit)
            self.tracing_worker.finished.connect(self.tracing_worker.deleteLater)
            self.tracing_worker.finished.connect(self.stop_temp)

            self.tracing_worker.newcurve.connect(lambda x: self.plot_area.newcurve(x))
            self.tracing_worker.plotdata.connect(lambda x: self.plot_area.plotdata(x))

            self.tracing_thread.start()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("No PSU for Vds has been setup")
            msg.setInformativeText("Press on one of the PSU buttons - red/gray buttons- to setup the PSU")
            msg.setWindowTitle("Vds missing")
            msg.setDetailedText("In the case that only 1 PSU will be used, it must be the Vds PSU not the Vgs")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def start_temperature_sensor(self):
        self.temperature_thread = QThread()
        self.temperature_worker = temperaturemonitor.TemperatureWorker()
        self.temperature_worker.moveToThread(self.temperature_thread)

        self.temperature_thread.started.connect(self.temperature_worker.start_temp_controller)
        self.temperature_thread.finished.connect(self.temperature_thread.deleteLater)
        self.temperature_worker.finished.connect(self.temperature_thread.quit)
        self.temperature_worker.finished.connect(self.temperature_worker.deleteLater)

        self.temperature_worker.temperature_data.connect(lambda x: self.dut_widgets.TemperatureIndicator.setText(str(x)))
        self.temperature_worker.temp_stable.connect(self.temperature_drift)

        self.temperature_thread.start()

    def stop_temp(self):
        self.stop_temperature_sensor.connect(self.temperature_worker.end_temperaturemonitor)
        self.stop_temperature_sensor.emit()

    def temperature_drift(self, status: bool):
        self.temperature_stable["status"] = status

    def getdata(self, data):
        self.data = data
        print("trace end")
        time.sleep(1)
        print("tracing thread " + str(self.tracing_thread.isRunning()))
        print("temperature thread " + str(self.temperature_thread.isRunning()))

    def freeze(self, freeze):
        self.psuVgsbutton.button.setDisabled(freeze)
        self.psuVdsbutton.button.setDisabled(freeze)
        self.PSUdict["Vgs PSU"].disablespinbxs(freeze)
        self.PSUdict["Vds PSU"].disablespinbxs(freeze)
        self.dut_widgets.TemperatureIndicator.setDisabled(freeze)
        self.dut_widgets.TempSpinbox.setDisabled(freeze)
        self.dut_widgets.DUTMaxPLabel.setDisabled(freeze)
        self.smoothcurveCheckB.setDisabled(freeze)
        self.plotlimitsCheckB.setDisabled(freeze)
        self.savecurvesB.setDisabled(freeze)

    def closeEvent(self, event):
        try:
            self.tracing_thread.requestInterruption()
            self.tracing_thread.quit()
            while self.tracing_thread.isRunning():
                print("waiting tracing_thread to end")
                time.sleep(1)
        except AttributeError:
            pass
        try:
            self.temperature_thread.stop_poller()
            self.temperature_thread.quit()
            while self.temperature_thread.isRunning():
                print("waiting temperature_thread to end")
                time.sleep(1)
        except AttributeError:
            pass

        self.PSUdict["Vgs PSU"].setvoltage(0)
        self.PSUdict["Vds PSU"].setvoltage(0)
        self.PSUdict["Vgs PSU"].enableoutput(False)
        self.PSUdict["Vds PSU"].enableoutput(False)
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


class DutSet(QWidget):
    def __init__(self):
        super().__init__()

        self.dutset_layout = QHBoxLayout()
        self.setLayout(self.dutset_layout)

        self.TemperatureLabel = QLabel("Tempr")
        self.TemperatureLabel.setMinimumSize(110, 50)
        self.dutset_layout.addWidget(self.TemperatureLabel)

        self.TemperatureIndicator = QLabel("0")
        self.TemperatureIndicator.setMinimumSize(110, 50)
        self.dutset_layout.addWidget(self.TemperatureIndicator)

        self.dutset_layout.addStretch()

        self.TempLabel = QLabel("Temp")
        self.TempLabel.setMinimumSize(80, 50)
        self.dutset_layout.addWidget(self.TempLabel)

        # self.layout.addStretch()
        self.TempSpinbox = QSpinBox()
        self.TempSpinbox.setMinimumSize(130, 50)
        self.TempSpinbox.setMaximumSize(130, 50)
        self.TempSpinbox.setMinimum(0)
        self.TempSpinbox.setMaximum(100)
        self.dutset_layout.addWidget(self.TempSpinbox)

        self.dutset_layout.addStretch()

        self.DUTMaxPLabel = QLabel("Max Power")
        self.DUTMaxPLabel.setMinimumSize(150, 50)
        self.dutset_layout.addWidget(self.DUTMaxPLabel)

        # self.layout.addStretch()
        self.DUTMaxPSpinbox = QSpinBox()
        self.DUTMaxPSpinbox.setMinimumSize(130, 50)
        self.DUTMaxPSpinbox.setMaximumSize(130, 50)
        self.DUTMaxPSpinbox.setMinimum(0)
        self.DUTMaxPSpinbox.setMaximum(300)
        self.dutset_layout.addWidget(self.DUTMaxPSpinbox)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
exit(app.exec_())
