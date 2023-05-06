import time

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QMessageBox


class Worker(QObject):
    newdata = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, _psudict, temperature_stable):
        super().__init__()
        self._PSUdict = _psudict
        self._VgsPSU = self._PSUdict["Vgs PSU"]
        self._VdsPSU = self._PSUdict["Vds PSU"]
        self._MaxP = self._PSUdict["DUT settings"].DUTMaxPSpinbox.value()
        self.temperature_stable = temperature_stable

    def traceroutine(self):

        if self._PSUdict["Heater PSU"].name != "Empty PSU":
            print("waiting to reach set temperature")
            while not self.temperature_stable["status"]:
                if self.thread().isInterruptionRequested():
                    self.stop()
                    return

        _VgsEND = self._VgsPSU.VENDwidget.widgetSpinbox.value()
        _VdsEND = self._VdsPSU.VENDwidget.widgetSpinbox.value()
        _IdsMAX = self._VdsPSU.IMAXwidget.widgetSpinbox.value()

        self._VdsPSU.setvoltage(0)
        self._VdsPSU.setcurrent(0)
        self._VdsPSU.enableoutput(True)
        _Vds = self._VdsPSU.VSTARTwidget.widgetSpinbox.value()

        if self._VgsPSU.name != "Empty PSU":
            self._VgsPSU.setvoltage(0)
            self._VgsPSU.setcurrent(0)
            self._VgsPSU.enableoutput(True)
        _Vgs = self._VgsPSU.VSTARTwidget.widgetSpinbox.value()
        _readVds = self._read_psu(self._VdsPSU, 3)

        while _Vgs <= _VgsEND:

            if self.thread().isInterruptionRequested():
                self.stop()
                return

            self.CheckStableTempandSetVoltage(self._VgsPSU, _Vgs)
            while _Vds <= _VdsEND:
                self._VdsPSU.setcurrent(min(_IdsMAX, self._MaxP / _Vds))

                if self.thread().isInterruptionRequested():
                    self.stop()
                    return

                self._VgsPSU.setvoltage(_Vgs)
                self.CheckStableTempandSetVoltage(self._VdsPSU, _Vds)
                _data = self._read_psu(self._VdsPSU, 3)
                _data.update({"Vgs": _Vgs})
                if _data["mode"] == "CC":
                    _data.update({"Vds": _Vds})
                    _VdsEND = _Vds - self._VdsPSU.STEPwidget.widgetSpinbox.value()
                self.newdata.emit(_data)

                # moveon = False
                # while moveon == False:
                #     msg = QMessageBox()
                #     msg.setIcon(QMessageBox.Information)
                #     msg.setText(str(_data))
                #     msg.setInformativeText("Press OK to retake the measurement or cancel to move on")
                #     msg.setWindowTitle("La")
                #     msg.setDetailedText("")
                #     msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                #     _response = msg.exec()
                #     if _response == QMessageBox.Cancel:
                #         moveon = True
                #     else:
                #         print(self._read_psu(self._VdsPSU, 3))

                _Vds += self._VdsPSU.STEPwidget.widgetSpinbox.value()

            _Vds = self._VdsPSU.VSTARTwidget.widgetSpinbox.value()
            _Vgs += self._VgsPSU.STEPwidget.widgetSpinbox.value()
        self.stop()

    def CheckStableTempandSetVoltage(self, _psu, _voltage):
        while not self.temperature_stable["status"]:
            self._VgsPSU.setvoltage(0)
            if self.thread().isInterruptionRequested():
                return
            print("waiting for temperature to stabilize***")
            time.sleep(1)
        _psu.setvoltage(_voltage)

    def _read_psu(self, _psu, times):
        reading = _psu.read(times)
        while reading["mode"] == "ERR":
            if self.temperature_stable["status"]:
                reading = _psu.read(times)
                print("current Drifting")
                print(reading)
        return reading

    def stop(self):
        self._VdsPSU.enableoutput(False)
        self._VdsPSU.setvoltage(0)
        self._VdsPSU.setcurrent(0)
        if self._VgsPSU.name != "Empty PSU":
            self._VgsPSU.enableoutput(False)
            self._VgsPSU.setvoltage(0)
            self._VgsPSU.setcurrent(0)
        self.finished.emit()

