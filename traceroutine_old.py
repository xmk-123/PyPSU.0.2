import time
import numpy as np

from plot import plotwin


def traceroutine(PSUdict, _MaxpwrSpinbox):   # args = psuVdsTestParameters, [psuVgsTestParameters]

    emmSTOP = False
    c = []

    _VgsPSU = PSUdict["Vgs PSU"]
    _VdsPSU = PSUdict["Vds PSU"]
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

    while _Vgs <= _VgsEND:
        _VgsPSU.setvoltage(_Vgs)
        while _Vds <= _VdsEND:
            _VdsPSU.setcurrent(min(_IdsMAX, _MaxpwrSpinbox.value()/(_Vds)))
            _VdsPSU.setvoltage(_Vds)
            _readVds = _VdsPSU.read(3)
            c.append([[_Vgs, _VdsPSU.polarity * _readVds["voltage"], _VdsPSU.polarity * _readVds["current"], _readVds["mode"]]])
            print(_VgsPSU.polarity * _Vgs, _VdsPSU.polarity * _readVds["voltage"], _VdsPSU.polarity * _readVds["current"], _readVds["mode"])

            if _readVds["mode"] == "CC":
                _VdsEND = _Vds - _VdsPSU.STEPwidget.widgetSpinbox.value()
            _Vds += _VdsPSU.STEPwidget.widgetSpinbox.value()
        _Vds = _VdsPSU.VSTARTwidget.widgetSpinbox.value()
        _Vgs += _VgsPSU.STEPwidget.widgetSpinbox.value()

