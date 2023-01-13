import time

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot


class Worker(QObject):
    plotdata = pyqtSignal(object)
    newcurve = pyqtSignal(float)
    finished = pyqtSignal(object)

    def __init__(self, _psudict, temperature_stable):
        super().__init__()
        self._PSUdict = _psudict
        self._MaxP = self._PSUdict["DUT settings"].DUTMaxPSpinbox.value()
        self.temperature_stable = temperature_stable

    @pyqtSlot()
    def traceroutine(self):

        self._data = None

        self._VgsPSU = self._PSUdict["Vgs PSU"]
        self._VdsPSU = self._PSUdict["Vds PSU"]

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

        _i = 0
        while _Vgs <= _VgsEND:
            if self._data is None:
                self._data = [[_Vgs, [0], [0], [""]]]
            else:
                self._data.append([_Vgs, [0], [0], [""]])

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
                _readVds = self._VdsPSU.read(3)
                print(_readVds)
                self._data[_i][1].append(self._VdsPSU.polarity * _readVds["voltage"])
                self._data[_i][2].append(self._VdsPSU.polarity * _readVds["current"])
                self._data[_i][3].append(self._VdsPSU.polarity * _readVds["mode"])
                self.plotdata.emit(self._data)
                if _readVds["mode"] == "CC":
                    _VdsEND = _Vds - self._VdsPSU.STEPwidget.widgetSpinbox.value()
                _Vds += self._VdsPSU.STEPwidget.widgetSpinbox.value()
            _Vds = self._VdsPSU.VSTARTwidget.widgetSpinbox.value()
            _Vgs += self._VgsPSU.STEPwidget.widgetSpinbox.value()
            _i += 1

        self._VdsPSU.enableoutput(False)
        self._VdsPSU.setvoltage(0)
        self._VdsPSU.setcurrent(0)
        if self._VgsPSU.name != "Empty PSU":
            self._VgsPSU.enableoutput(False)
            self._VgsPSU.setvoltage(0)
            self._VgsPSU.setcurrent(0)

        self.finished.emit(self._data)

    def SetVoltageAndCheckStableTemp(self, _psu, _voltage):
        _psu.setvoltage(_voltage)
        while not self.temperature_stable["status"]:
            if self.thread().isInterruptionRequested():
                self.stop()
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
        print("ZEROED Voltages")

        self.finished.emit(self._data)






