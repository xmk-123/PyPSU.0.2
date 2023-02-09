import sys
import time

from PyQt5.QtCore import pyqtSignal, QThread
from match_win import MatchWindow
from plot import PlotWin
from setup import PsuInitWindow
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QWidget,
                             QPushButton, QVBoxLayout, QLabel, QSpinBox, QFrame,
                             QSizePolicy, QCheckBox, QMenu, QAction, QMessageBox, QFileDialog, QTabWidget, qApp)
import traceroutine
from powersupply_EMPTY import EmptyPSU
from VirtualPSU import VirtualPSU
from temperature_controller import TemperatureWorker

ask_to_save = True


class MainWindow(QMainWindow):

    update_pid_last_output = pyqtSignal(float)

    def __init__(self):
        super().__init__()

        # self.showMaximized()
        self.PSUdict = {"Vgs PSU": VirtualPSU([EmptyPSU()]),
                        "Vds PSU": VirtualPSU([EmptyPSU()]),
                        "Heater PSU": VirtualPSU([EmptyPSU()]),
                        "Temperature Sensor": None}
        self.temperature_stable = {"status": False}
        self.last_saved = True
        self.ask_to_save = True

        self.PsuSetupWin = PsuInitWindow(self.PSUdict)
        self.PsuSetupWin.Vgspolaritychanged.connect(lambda s: self.psuVgsbutton.set_polarity(s))
        self.PsuSetupWin.Vdspolaritychanged.connect(lambda s: self.psuVdsbutton.set_polarity(s))
        self.PsuSetupWin.updateMainWindow.connect(self.buildui)

        self.data = {}
        self.match_w = MatchWindow()
        self.buildui()

        _menuBar = self.menuBar()
        file_menu = QMenu("&Menu", self)
        _menuBar.addMenu(file_menu)

        _savesettingsMenuItem = QAction(QIcon(), '&Save startup Settings', self)
        # _savesettingsMenuItem.setStatusTip('New document')
        _savesettingsMenuItem.triggered.connect(self.PsuSetupWin.savesettings)
        file_menu.addAction(_savesettingsMenuItem)

        _clearsettingsMenuItem = QAction(QIcon(), '&Clear startup Settings', self)
        # _clearsettingsMenuItem.setStatusTip('New document')
        _clearsettingsMenuItem.triggered.connect(lambda: self.PsuSetupWin.settings.clear())
        file_menu.addAction(_clearsettingsMenuItem)

        _resetasktosave = QAction(QIcon(), '&Reset save last trace warning', self)
        _resetasktosave.triggered.connect(self.reset_ask_to_save)
        file_menu.addAction(_resetasktosave)

        self.PsuSetupWin.applysettings()

    def reset_ask_to_save(self):
        self.ask_to_save = True

    def buildui(self):
        
        self.setWindowTitle("Curvetrace 0.3")
        self.window = QWidget()
        _mainlayout = QVBoxLayout()
        self.window.setLayout(_mainlayout)

        _tabs = QTabWidget()
        _tabs.addTab(self.window, "Trace")
        _tabs.addTab(self.match_w, "Match")
        self.setCentralWidget(_tabs)

        _layouttopH = QHBoxLayout()
        _layoutbottomV = QVBoxLayout()

        _layouttopcenterV = QVBoxLayout()

        _layouttopcentertopH = QHBoxLayout()
        _layouttopcentermiddleH = QHBoxLayout()
        _layouttopcenterbottomH = QHBoxLayout()

        _layoutbottomH = QHBoxLayout()

    # top center pane start

        self.PsuVgsLabel = QLabel(self.PSUdict["Vgs PSU"].name)
        self.PsuVgsLabel.setMinimumSize(110, 50)
        _layouttopcentertopH.addWidget(self.PsuVgsLabel)

        _layouttopcentertopH.addStretch()

        self.PsuVdsLabel = QLabel(self.PSUdict["Vds PSU"].name)
        self.PsuVdsLabel.setMinimumSize(110, 50)
        _layouttopcentertopH.addWidget(self.PsuVdsLabel)

        # top center top end
        # top center middle start

        self.psuVgsbutton = PsuButtonBox()
        _layouttopcentermiddleH.addWidget(self.psuVgsbutton)
        self.psuVgsbutton.PsuButtonPressed.connect(self.PsuSetupWin.show)

        _layouttopcentermiddleH.addStretch()

        self.start_tracing_button = QPushButton()
        self.start_tracing_button.setObjectName("start_tracing_button")
        self.start_tracing_button.setMinimumSize(150, 150)
        self.start_tracing_button.clicked.connect(self.start_tracing)
        self.start_tracing_button.setIcon(QIcon('Nmos.png'))

        self.start_tracing_button.setIconSize(QtCore.QSize(130, 130))
        _layouttopcentermiddleH.addWidget(self.start_tracing_button)

        self.stop_button = QPushButton()
        self.stop_button.setObjectName("stop_tracing_button")
        self.stop_button.setMinimumSize(150, 150)
        self.stop_button.clicked.connect(self.stop_tracing)
        self.stop_button.setIcon(QIcon('stop-sign.png'))
        self.stop_button.setDisabled(True)

        self.stop_button.setIconSize(QtCore.QSize(130, 130))
        _layouttopcentermiddleH.addWidget(self.stop_button)

        _layouttopcentermiddleH.addStretch()

        self.psuVdsbutton = PsuButtonBox()
        _layouttopcentermiddleH.addWidget(self.psuVdsbutton)
        self.psuVdsbutton.PsuButtonPressed.connect(self.PsuSetupWin.show)
        # top center middle end

        # top center bottom start
        self.dut_widgets = DutSet()
        _layouttopcenterbottomH.addWidget(self.dut_widgets)
        self.PSUdict["DUT settings"] = self.dut_widgets
        # top center bottom end
    # top center pane end

    # bottom start
        self.plot_area = PlotWin()
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator.setLineWidth(3)

        _layoutbottomV.addWidget(separator)

        self.smoothcurveCheckB = QCheckBox("Smooth Curves")
        self.smoothcurveCheckB.toggled.connect(lambda x: self.plot_area.smoothcurves(self.data, x))
        _layoutbottomH.addWidget(self.smoothcurveCheckB)

        self.plotlimitsCheckB = QCheckBox("Plot Power lim")
        self.plotlimitsCheckB.toggled.connect(lambda x: self.plot_area.plotlimits(self.dut_widgets.DUTMaxPSpinbox.value(),
                                                                                  self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.value(),
                                                                                  self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.value(),
                                                                                  x))
        _layoutbottomH.addWidget(self.plotlimitsCheckB)

        self.savecurvesB = QPushButton("Save")
        self.savecurvesB.setMinimumSize(130, 50)
        self.savecurvesB.setMaximumSize(130, 50)
        self.savecurvesB.pressed.connect(self.savecurves)
        _layoutbottomH.addWidget(self.savecurvesB)
    # bottom end

        _layouttopH.addWidget(self.PSUdict["Vgs PSU"].PSUwindow)
        _layouttopH.addStretch()

        _layouttopcenterV.addLayout(_layouttopcentertopH)
        _layouttopcenterV.addLayout(_layouttopcentermiddleH)
        _layouttopcenterV.addLayout(_layouttopcenterbottomH)

        _layouttopH.addLayout(_layouttopcenterV, 0)

        _layouttopH.addStretch()
        _layouttopH.addWidget(self.PSUdict["Vds PSU"].PSUwindow)

        _mainlayout.addLayout(_layouttopH, 0)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        # separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator.setLineWidth(3)

        _mainlayout.addWidget(separator)
        _mainlayout.addLayout(_layoutbottomH)
        _mainlayout.addWidget(self.plot_area)

    def savecurves(self):
        saveFile = QFileDialog.getSaveFileName()[0]
        with open(saveFile, 'w') as f:
            f.write(str(self.data))
        self.last_saved = True

    def start_tracing(self):
        if self.PSUdict["Vds PSU"].name != "Empty PSU":
            if not self.last_saved and self.ask_to_save:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)

                msg.setText("Last trace has not been saved")
                msg.setInformativeText("Data will be lost. Want to proceed?")
                msg.setWindowTitle("Last trace has not been saved")
                msg.setDetailedText("")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                cb = QCheckBox("Don't ask again.")
                msg.setCheckBox(cb)
                _response = msg.exec()
                self.ask_to_save = not cb.isChecked()
                if _response == QMessageBox.Cancel:
                    return
            self.start_tracing_button.setDisabled(True)
            self.stop_button.setDisabled(False)
            self.last_saved = False
            self.start_temperature_controller()
            self.freeze(True)
            self.plot_area.reset()
            self.data.clear()

            self.tracing_thread = QThread()
            self.tracing_worker = traceroutine.Worker(self.PSUdict, self.temperature_stable)
            self.tracing_worker.moveToThread(self.tracing_thread)

            self.tracing_thread.started.connect(self.tracing_worker.traceroutine)
            self.tracing_thread.finished.connect(self.tracing_thread.deleteLater)

            self.tracing_worker.finished.connect(self.tracing_end)
            self.tracing_worker.finished.connect(self.tracing_thread.quit)
            self.tracing_worker.finished.connect(self.tracing_worker.deleteLater)

            self.tracing_worker.newdata.connect(lambda x: self.new_data_received(x))
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

    def tracing_end(self):
        # print(str(self.data).replace("]],", "]],\n"))
        self.stop_button.setDisabled(True)
        self.freeze(False)
        if self.PSUdict["Temperature Sensor"] is not None:
            self.temperature_thread.requestInterruption()
        self.start_tracing_button.setDisabled(False)

    def new_data_received(self, new_data):
        if str(new_data["Vgs"]) not in self.data.keys():
            self.data.update({str(new_data["Vgs"]): [[0], [0], [""]]})

        self.data[str(new_data["Vgs"])][0].append(self.PSUdict["Vds PSU"].polarity * new_data["voltage"])
        self.data[str(new_data["Vgs"])][1].append(self.PSUdict["Vds PSU"].polarity * new_data["current"])
        self.data[str(new_data["Vgs"])][2].append(self.PSUdict["Vds PSU"].polarity * new_data["mode"])

        self.plot_area.plotdata(self.data)

    def start_temperature_controller(self):
        if self.PSUdict["Temperature Sensor"] is None:
            self.temperature_stable["status"] = True
            self.dut_widgets.TemperatureIndicator.setText("N/A")
        else:
            self.temperature_thread = QThread()
            self.temperature_worker = TemperatureWorker(self.PSUdict, self.dut_widgets.TempSpinbox.value())
            self.temperature_worker.moveToThread(self.temperature_thread)

            self.temperature_thread.started.connect(self.temperature_worker.start_temp_controller)
            self.temperature_thread.finished.connect(self.temperature_thread.deleteLater)
            self.temperature_worker.finished.connect(self.temperature_thread.quit)
            self.temperature_worker.finished.connect(self.temperature_worker.deleteLater)

            self.temperature_worker.temperature_data.connect(lambda x: self.dut_widgets.TemperatureIndicator.setText(str(x)))
            self.temperature_worker.temp_stable.connect(lambda x: self.temperature_stable.update({"status": x}))

            self.temperature_thread.start()

    def stop_tracing(self):
        try:
            self.tracing_thread.requestInterruption()
            self.tracing_thread.quit()
            # self.tracing_thread.wait(3)
            while self.tracing_thread.isRunning():
                print("waiting tracing_thread to end")
                time.sleep(0.1)
        except (AttributeError, RuntimeError) as e:
            print(e)
            pass

        try:
            self.temperature_thread.requestInterruption()
            time.sleep(3)
            self.temperature_thread.quit()
            while self.temperature_thread.isRunning():
                print("waiting temperature_thread to end")
                time.sleep(0.1)
        except (AttributeError, RuntimeError) as e:
            print(e)
            pass

        self.PSUdict["Vgs PSU"].setvoltage(0)
        self.PSUdict["Vds PSU"].setvoltage(0)
        self.PSUdict["Heater PSU"].setvoltage(0)
        self.PSUdict["Vgs PSU"].enableoutput(False)
        self.PSUdict["Vds PSU"].enableoutput(False)
        self.PSUdict["Heater PSU"].enableoutput(False)
        self.PSUdict["Vgs PSU"].setcurrent(0)
        self.PSUdict["Vds PSU"].setcurrent(0)
        self.PSUdict["Heater PSU"].setcurrent(0)

    def closeEvent(self, event):
        self.stop_tracing()
        self.PsuSetupWin.deleteLater()

    def freeze(self, freeze):
        self.psuVgsbutton.button.setDisabled(freeze)
        self.psuVdsbutton.button.setDisabled(freeze)
        self.PSUdict["Vgs PSU"].disablespinbxs(freeze)
        self.PSUdict["Vds PSU"].disablespinbxs(freeze)
        self.dut_widgets.TemperatureIndicator.setDisabled(freeze)
        self.dut_widgets.TempSpinbox.setDisabled(freeze)
        self.dut_widgets.DUTMaxPSpinbox.setDisabled(freeze)
        self.smoothcurveCheckB.setDisabled(freeze)
        self.plotlimitsCheckB.setDisabled(freeze)
        self.savecurvesB.setDisabled(freeze)


class PsuButtonBox(QWidget):

    PsuButtonPressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        _layout = QVBoxLayout()
        self.button = QPushButton()
        self.set_polarity(True)
        self.button.setMinimumSize(150, 65)
        _layout.addWidget(self.button)
        self.setLayout(_layout)

        self.button.clicked.connect(self.PsuButtonPressed.emit)

    def set_polarity(self, value):
        if value:
            stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 red, stop: 0.51 dimgrey)}"
            self.button.setStyleSheet(stylesheet)
            self.button.setText("+                  +\nPSU\n-                 -")
        else:
            stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 dimgrey, stop: 0.51 red)}"
            self.button.setStyleSheet(stylesheet)
            self.button.setText("-                  -\nPSU\n+                 +")


class DutSet(QWidget):
    def __init__(self):
        super().__init__()

        _dutset_layout = QHBoxLayout()
        self.setLayout(_dutset_layout)

        _TemperatureLabel = QLabel("Temp Now")
        _TemperatureLabel.setMinimumSize(110, 50)
        _dutset_layout.addWidget(_TemperatureLabel)

        self.TemperatureIndicator = QLabel("N/A")
        self.TemperatureIndicator.setMinimumSize(110, 50)
        _dutset_layout.addWidget(self.TemperatureIndicator)

        _dutset_layout.addStretch()

        _TempLabel = QLabel("Set Temp")
        _TempLabel.setMinimumSize(80, 50)
        _dutset_layout.addWidget(_TempLabel)

        # self.layout.addStretch()
        self.TempSpinbox = QSpinBox()
        self.TempSpinbox.setMinimumSize(130, 50)
        self.TempSpinbox.setMaximumSize(130, 50)
        self.TempSpinbox.setMinimum(0)
        self.TempSpinbox.setMaximum(100)

        _dutset_layout.addWidget(self.TempSpinbox)

        _dutset_layout.addStretch()

        _DUTMaxPLabel = QLabel("Max Power")
        _DUTMaxPLabel.setMinimumSize(150, 50)
        _dutset_layout.addWidget(_DUTMaxPLabel)

        # self.layout.addStretch()
        self.DUTMaxPSpinbox = QSpinBox()
        self.DUTMaxPSpinbox.setMinimumSize(130, 50)
        self.DUTMaxPSpinbox.setMaximumSize(130, 50)
        self.DUTMaxPSpinbox.setMinimum(0)
        self.DUTMaxPSpinbox.setMaximum(300)
        _dutset_layout.addWidget(self.DUTMaxPSpinbox)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
exit(app.exec_())
