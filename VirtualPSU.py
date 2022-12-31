from PyQt5.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QWidget, QVBoxLayout
from powersupply_EMPTY import EmptyPSU
import time
import numpy as np
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class VirtualPSU(QWidget):

    def __init__(self, _physical_psu_objects_list):
        super().__init__()
        self.physical_psu_objects_list = _physical_psu_objects_list
        match len(self.physical_psu_objects_list):
            case 1:
                self._multiple_physical_PSUs = False
            case _ if len(_physical_psu_objects_list) > 1:
                self._multiple_physical_PSUs = True
            case _:
                raise TypeError("Missing physical PSU argument in VirtualPSU class creation")

        if self._multiple_physical_PSUs:
            self.VMIN = sum([i.VMIN for i in self.physical_psu_objects_list])
            self.VMAX = sum([i.VMAX for i in self.physical_psu_objects_list])
            self.VRESSET = min([i.VRESSET for i in self.physical_psu_objects_list])
            if self.VRESSET < 1:
                self.VRESSETCNT = len(str(self.VRESSET).split(".")[1])
            else:
                self.VRESSETCNT = 0

            self.IMAX = min([i.IMAX for i in self.physical_psu_objects_list])
            self.IRESSET = max([i.IRESSET for i in self.physical_psu_objects_list])
            if self.IRESSET < 1:
                self.IRESSETCNT = len(str(self.IRESSET).split(".")[1])
            else:
                self.IRESSETCNT = 0

            self.VRESSETCNTMAX = max([i.VRESSETCNT for i in self.physical_psu_objects_list])    # max _voltage resolution of physical psu s

            self.INDEX_OF_PPSU_VRESSETCNTMAX = ([i.VRESSETCNT for i in self.physical_psu_objects_list].index(self.VRESSETCNTMAX))   # physical psu with max resolution
            self.VMAXLIST = [i.VMAX for i in self.physical_psu_objects_list]
            self._PCT_DISTRIBUTION = [i * 100 / sum(self.VMAXLIST) for i in self.VMAXLIST]
            self.IRESSETCNTMAX = min([i.IRESSETCNT for i in self.physical_psu_objects_list])  # min current resolution of physical psu s
            self.PMAX = sum([i.PMAX for i in self.physical_psu_objects_list])
            self.name = "\n".join([str(count + 1) + ")" + n.name for count, n in enumerate(self.physical_psu_objects_list)])
        else:
            self.VMIN = self.physical_psu_objects_list[0].VMIN
            self.VMAX = self.physical_psu_objects_list[0].VMAX
            self.VRESSET = self.physical_psu_objects_list[0].VRESSET
            if self.VRESSET < 1:
                self.VRESSETCNT = len(str(self.VRESSET).split(".")[1])
            else:
                self.VRESSETCNT = 0

            self.IMAX = self.physical_psu_objects_list[0].IMAX
            self.IRESSET = self.physical_psu_objects_list[0].IRESSET
            if self.IRESSET < 1:
                self.IRESSETCNT = len(str(self.IRESSET).split(".")[1])
            else:
                self.IRESSETCNT = 0
            self.PMAX = self.physical_psu_objects_list[0].PMAX
            self.name = self.physical_psu_objects_list[0].name

        if self.VRESSET > 0:

            self.PSUwindow = QWidget()
            self._PSUlayout = QVBoxLayout()
            self.PSUwindow.setLayout(self._PSUlayout)
            self.polarity = True
            self.VSTARTwidget = ParameterWidget("Start V", max(self.VMIN, self.VRESSET), self.VMAX, self.VRESSET, self.VRESSETCNT)
            self.VENDwidget = ParameterWidget("End V", max(self.VMIN, self.VRESSET), self.VMAX, self.VRESSET, self.VRESSETCNT)
            self.STEPwidget = ParameterWidget("Step V", self.VRESSET, self.VMAX, self.VRESSET, self.VRESSETCNT)
            self.IMAXwidget = ParameterWidget("Max I", 0, self.IMAX, self.IRESSET, self.IRESSETCNT)

            self._PSUlayout.addWidget(self.VSTARTwidget)
            self._PSUlayout.addWidget(self.VENDwidget)
            self._PSUlayout.addWidget(self.STEPwidget)
            self._PSUlayout.addWidget(self.IMAXwidget)

            self.VSTARTwidget.widgetSpinbox.valueChanged.connect(self.Vstartconditions)
            self.VENDwidget.widgetSpinbox.valueChanged.connect(self.Vendconditions)

            self.disablespinbxs(_physical_psu_objects_list[0].name == "Empty PSU")

    def Vstartconditions(self, value):
        if value > self.VENDwidget.widgetSpinbox.value():
            self.VENDwidget.widgetSpinbox.setValue(self.VSTARTwidget.widgetSpinbox.value())

    def Vendconditions(self, value):
        if value < self.VSTARTwidget.widgetSpinbox.value():
            self.VSTARTwidget.widgetSpinbox.setValue(self.VENDwidget.widgetSpinbox.value())

    def disablespinbxs(self, disable):
        for widget in self._PSUlayout.parentWidget().findChildren(QDoubleSpinBox):
            widget.setDisabled(disable)

    def setvoltage(self, _voltage):
        if self._multiple_physical_PSUs:
            if (_voltage <= self.VMAX) and (_voltage >= self.VMIN):
                _voltage_list = [i * _voltage for i in self._PCT_DISTRIBUTION]    # split _voltage according to max _voltage of each physical psu
                fractional = 0
                for count, v in enumerate(_voltage_list):
                    if count == self.INDEX_OF_PPSU_VRESSETCNTMAX:   # skip the psu with the highest resolution
                        pass
                    else:
                        fractional += (v % 1)                   # sum all fractional parts of voltages except the _voltage of the psu with the highest resolution
                        _voltage_list[count] = v - fractional    # remove the fractional part of the set _voltage of each ppsu except of the psu with the highest resolution
                _voltage_list[self.INDEX_OF_PPSU_VRESSETCNTMAX] = _voltage_list[self.INDEX_OF_PPSU_VRESSETCNTMAX] + fractional    # add the sum of the fractional parts to the ppsu with the highest resolutio
                _set_voltage = tuple(zip(self.physical_psu_objects_list, _voltage_list))

                # set the voltage of each physical PSU:
                for p, v in _set_voltage:
                    p.setvoltage(v)
                return 0
            else:
                logging.warning("_voltage setting out of bounds "
                                + self.VMAX + " max / " + self.VMIN + " min ")
                return 1
        else:
            self.physical_psu_objects_list[0].setvoltage(_voltage)

    def setcurrent(self, _current):
        if self._multiple_physical_PSUs:
            _current = round(_current, self.IRESSETCNTMAX)
            if (_current <= self.IMAX) and (_current >= self.IMIN):
                for p in self.physical_psu_objects_list:
                    p.setcurrent(_current)
                return 0
            else:
                logging.warning("current setting out of bounds "
                                + self.IMAX + " max / " + self.IMIN + " min ")
                return 1
        else:
            self.physical_psu_objects_list[0].setcurrent(_current)

    def turnoff(self):
        for p in self.physical_psu_objects_list:
            p.output(False)
            p.voltage(self.VMIN)
            p.current(0.0)

    def turnon(self):
        for p in self.physical_psu_objects_list:
            p.output(True)

    def read(self, n=1):
        if self._multiple_physical_PSUs:
            if n < 1:
                raise RuntimeError('Number of consistent readings in a row must be larger than 1!')

            t0 = time.time()
            match = 0
            v = 0
            vsum = 0
            i = 0
            isum = 0
            limt = []

            while match < n:
                for p in self.physical_psu_objects_list:
                    vv, ii, ll = p._reading()
                    vsum += vv
                    isum += ii
                    limt.append(ll)
                if (vsum == v) and (isum == i):
                    match += 1
                else:
                    v = vsum
                    i = isum
                    time.sleep(self.READIDLETIME)

                if time.time() - t0 > self.MAXSETTLETIME:
                    # getting consistent readings is taking too long; give up
                    logger.info(self.__name__ + ': Could not get ' + str(n) + ' consistent readings in a row after ' + str(
                        self.MAXSETTLETIME) + ' s! DUT drifting? Noise?')
                    break
            if n > 1:
                v = np.mean(v)
                i = np.mean(i)

            return v, i, limt
        else:
            return self.physical_psu_objects_list[0].read(n)


class ParameterWidget(QWidget):
    def __init__(self, name, minval, maxval, minstep, resolution):
        super().__init__()
        self._PSUlayout2 = QHBoxLayout()

        self._widgetLabel = QLabel(name)
        self._widgetLabel.setMinimumSize(110, 50)
        self._PSUlayout2.addWidget(self._widgetLabel)

        self.widgetSpinbox = QDoubleSpinBox()
        self.widgetSpinbox.setMinimumSize(130, 50)
        self.widgetSpinbox.setMaximumSize(130, 50)
        self.widgetSpinbox.setMinimum(minval)
        self.widgetSpinbox.setMaximum(maxval)
        self.widgetSpinbox.setSingleStep(minstep)
        self.widgetSpinbox.setDecimals(resolution)
        self._PSUlayout2.addWidget(self.widgetSpinbox)

        self.setLayout(self._PSUlayout2)



