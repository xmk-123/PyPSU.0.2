from PyQt5.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QWidget, QVBoxLayout
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
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
                raise TypeError(" physical PSU argument in VirtualPSU object creation")

        if self._multiple_physical_PSUs:
            self.VMIN = sum([i.VMIN for i in self.physical_psu_objects_list])
            self.VMAX = sum([i.VMAX for i in self.physical_psu_objects_list])
            self.VOFFSETMAX = sum([i.VOFFSETMAX for i in self.physical_psu_objects_list])
            self.VRESSET = min([i.VRESSET for i in self.physical_psu_objects_list])
            if self.VRESSET < 1:
                self.VRESSETCNT = len(str(self.VRESSET).split(".")[1])
            else:
                self.VRESSETCNT = 0

            self.IMAX = min([i.IMAX for i in self.physical_psu_objects_list])
            self.IOFFSETMAX = max([i.IOFFSETMAX for i in self.physical_psu_objects_list])
            self.IRESSET = max([i.IRESSET for i in self.physical_psu_objects_list])
            if self.IRESSET < 1:
                self.IRESSETCNT = len(str(self.IRESSET).split(".")[1])
            else:
                self.IRESSETCNT = 0

            self.VRESSETCNTMAX = max([i.VRESSETCNT for i in self.physical_psu_objects_list])    # max _voltage resolution of physical psu s
            self.INDEX_OF_PPSU_VRESSETCNTMAX = ([i.VRESSETCNT for i in self.physical_psu_objects_list].index(self.VRESSETCNTMAX))   # physical psu with max resolution

            self._VMAXLIST = [i.VMAX for i in self.physical_psu_objects_list]
            self._PCT_DISTRIBUTION_LIST = [i / sum(self._VMAXLIST) for i in self._VMAXLIST]  # list of percentage of voltage eacu psu will carry

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

        logger.info('\n' +
                    'VRESSETCNTMAX = ' + str(self.VRESSETCNT) + '\n' +
                    'VMIN = ' + str(self.VMIN) + '\n' +
                    'VMAX = ' + str(self.VMAX) + '\n' +
                    'IMAX = ' + str(self.IMAX) + '\n' +
                    'PMAX = ' + str(self.PMAX) + '\n' +
                    'NAME = ' + self.name + '\n')

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
            if self.VMIN <= _voltage <= self.VMAX:
                _voltage_list = [i * _voltage for i in self._PCT_DISTRIBUTION_LIST]    # split _voltage according to max _voltage of each physical psu
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
            if _current <= self.IMAX:
                for p in self.physical_psu_objects_list:
                    p.setcurrent(_current)
                return 0
            else:
                logging.warning("current setting out of bounds "
                                + self.IMAX + " max / " + self.IMIN + " min ")
                return 1
        else:
            self.physical_psu_objects_list[0].setcurrent(_current)

    def enableoutput(self, setting: bool):
        for p in self.physical_psu_objects_list:
            p.output(setting)
            if not set:
                p.voltage(self.VMIN)
                p.current(0.0)

    def read(self, n=1):
        if self._multiple_physical_PSUs:
            if n < 1:
                raise RuntimeError('Number of consistent readings in a row must be larger than 1!')
            vsum, vv, ii = 0.0, 0.0, 0.0

            i = []
            limt = []

            for p in self.physical_psu_objects_list:
                readings = p.physical_psu_readings()
                vsum += readings["voltage"]
                i.append(readings["current"])
                limt.append(readings["mode"])
            if "ERR" in limt:
                ll = "ERR"
            else:
                if "CC" in limt:
                    ll = "CC"
                else:
                    ll = "CV"
            if not all(current - self.IOFFSETMAX <= i[0] <= current + self.IOFFSETMAX for current in i):
                logger.error("Unequal current readings between chained PSUs")
            ii = i[0]
            return dict(zip(("voltage", "current", "mode"), (vsum, ii, ll)))
        else:
            return self.physical_psu_objects_list[0].physical_psu_readings(n)


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
