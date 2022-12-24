import time

from PyQt5.QtCore import pyqtSignal, QObject


class worker(QObject):
    finished = pyqtSignal()
    updateplot = pyqtSignal(object)
    newcurve = pyqtSignal(float)
    def __init__(self, _PSUdict, data,  _MaxpwrSpinbox):
        super().__init__()
        self._PSUdict = _PSUdict
        self._MaxpwrSpinbox = _MaxpwrSpinbox
        self.data = data

    def traceroutine(self):

        emmSTOP = False
        self.data = None

        _VgsPSU = self._PSUdict["Vgs PSU"]
        _VdsPSU = self._PSUdict["Vds PSU"]
        _VgsEND = _VgsPSU.VENDwidget.widgetSpinbox.value()
        _VdsEND = _VdsPSU.VENDwidget.widgetSpinbox.value()
        _IdsMAX = _VdsPSU.IMAXwidget.widgetSpinbox.value()

        _VdsPSU.setvoltage(0)
        _VdsPSU.setcurrent(0)
        _VdsPSU.turnon()
        _Vds = _VdsPSU.VSTARTwidget.widgetSpinbox.value()

        if _VgsPSU.name != "Empty PSU":
            _VgsPSU.setvoltage(0)
            _VgsPSU.setcurrent(0)
            _VgsPSU.turnon()
        _Vgs = _VgsPSU.VSTARTwidget.widgetSpinbox.value()
        _readVds = _VdsPSU.read(3)

        _i = 0
        while _Vgs <= _VgsEND:
            if self.data is None:
                self.data = [[_Vgs, [0], [0], [""]]]
            else:
                self.data.append([_Vgs, [0], [0], [""]])

            _VgsPSU.setvoltage(_Vgs)
            self.newcurve.emit(_Vgs)
            while _Vds <= _VdsEND:
                _VdsPSU.setcurrent(min(_IdsMAX, self._MaxpwrSpinbox.value() / (_Vds)))
                _VdsPSU.setvoltage(_Vds)
                _readVds = _VdsPSU.read(3, _Vgs)
                self.data[_i][1].append(_VdsPSU.polarity * _readVds["voltage"])
                self.data[_i][2].append(_VdsPSU.polarity * _readVds["current"])
                self.data[_i][3].append(_VdsPSU.polarity * _readVds["mode"])
                print(self.data)
                self.updateplot.emit(self.data)
                time.sleep(0.1) #  ****************************************************     remove
                if _readVds["mode"] == "CC":
                    _VdsEND = _Vds - _VdsPSU.STEPwidget.widgetSpinbox.value()
                _Vds += _VdsPSU.STEPwidget.widgetSpinbox.value()
            _Vds = _VdsPSU.VSTARTwidget.widgetSpinbox.value()
            _Vgs += _VgsPSU.STEPwidget.widgetSpinbox.value()
            _i += 1
        c = []
        self.finished.emit()

