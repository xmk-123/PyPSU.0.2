import time

from PyQt5.QtCore import pyqtSignal, QObject


class worker(QObject):
    finished = pyqtSignal()
    updateplot = pyqtSignal(object)

    def __init__(self, _PSUdict, _MaxpwrSpinbox, _graphWidget):
        super().__init__()
        self._PSUdict = _PSUdict
        self._MaxpwrSpinbox = _MaxpwrSpinbox
        self._graphWidget = _graphWidget

    def traceroutine(self):

        emmSTOP = False
        c = [[0, [0], [0], ""]]

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

        _i = 1
        while _Vgs <= _VgsEND:
            c.append([_Vgs, [0], [0], [""]])
            _VgsPSU.setvoltage(_Vgs)
            while _Vds <= _VdsEND:
                _VdsPSU.setcurrent(min(_IdsMAX, self._MaxpwrSpinbox.value() / (_Vds)))
                _VdsPSU.setvoltage(_Vds)
                _readVds = _VdsPSU.read(3)
                c[_i][1].append(_VdsPSU.polarity * _readVds["voltage"])
                c[_i][2].append(_VdsPSU.polarity * _readVds["current"])
                c[_i][3].append(_VdsPSU.polarity * _readVds["mode"])
                # print(_VgsPSU.polarity * _Vgs, _VdsPSU.polarity * _readVds["voltage"], _VdsPSU.polarity * _readVds["current"], _readVds["mode"])
                # print(c[_i])
                self.updateplot.emit(c[_i])
                time.sleep(0.5)
                if _readVds["mode"] == "CC":
                    _VdsEND = _Vds - _VdsPSU.STEPwidget.widgetSpinbox.value()
                _Vds += _VdsPSU.STEPwidget.widgetSpinbox.value()
            _Vds = _VdsPSU.VSTARTwidget.widgetSpinbox.value()
            _Vgs += _VgsPSU.STEPwidget.widgetSpinbox.value()
            _i += 1
        c = []
        self.finished.emit()

