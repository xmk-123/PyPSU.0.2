import time

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot


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

    @pyqtSlot()
    def traceroutine(self):

        if self._PSUdict["Heater PSU"].name != "Empty PSU":
            while not self.temperature_stable["status"]:
                print("warming up")

                if self.thread().isInterruptionRequested():
                    print("0000000000000000000")
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
        _readVds = self._VdsPSU.read(3)

        while _Vgs <= _VgsEND:
            _new_curve = True

            if self.thread().isInterruptionRequested():
                self.stop()
                return

            self.SetVoltageAndCheckStableTemp(self._VgsPSU, _Vgs)
            while _Vds <= _VdsEND:
                self._VdsPSU.setcurrent(min(_IdsMAX, self._MaxP / _Vds))

                if self.thread().isInterruptionRequested():
                    self.stop()
                    return

                self.SetVoltageAndCheckStableTemp(self._VdsPSU, _Vds)
                _data = self._VdsPSU.read(3)
                _data.update({"Vgs": _Vgs, "New curve": _new_curve})
                if _new_curve:
                    _new_curve = False
                self.newdata.emit(_data)

                if _readVds["mode"] == "CC":
                    _VdsEND = _Vds - self._VdsPSU.STEPwidget.widgetSpinbox.value()
                _Vds += self._VdsPSU.STEPwidget.widgetSpinbox.value()

            _Vds = self._VdsPSU.VSTARTwidget.widgetSpinbox.value()
            _Vgs += self._VgsPSU.STEPwidget.widgetSpinbox.value()
        self.stop()

    def SetVoltageAndCheckStableTemp(self, _psu, _voltage):
        _psu.setvoltage(_voltage)
        while not self.temperature_stable["status"]:
            if self.thread().isInterruptionRequested():
                return
            print("waiting for temperature to stabilize")
            time.sleep(1)

    def stop(self):
        self._VdsPSU.enableoutput(False)
        self._VdsPSU.setvoltage(0)
        self._VdsPSU.setcurrent(0)
        if self._VgsPSU.name != "Empty PSU":
            self._VgsPSU.enableoutput(False)
            self._VgsPSU.setvoltage(0)
            self._VgsPSU.setcurrent(0)
        self.finished.emit()

