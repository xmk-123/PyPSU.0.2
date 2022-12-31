"""
Python class for composite power supply objects.
"""

import time
import numpy as np
import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDoubleSpinBox, QHBoxLayout, QLabel

logger = logging.getLogger('powersupply')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# PSU object:
#    .setVoltage(voltage)   set voltage
#    .setCurrent(current)   set current
#    .turnOff()   	    turn PSU output off
#    .turnOn()   	    turn PSU output on
#    .read()                read current voltage, current, and limiter mode (voltage or current limiter active)
#    .settletime()          estimated settle time to attain stable voltage + current at PSU output
#                               after changing the setpoint (s)
#    .VMAX                  max. supported voltage (V)
#    .VMIN                  min. supported voltage (V)
#    .IMAXwidget                  max. supported current (V)
#    .PMAX                  max. supported power (W)
#    .VRESSET               resolution of voltage setting (V)
#    .IRESSET               resolution of current setting (A)
#    .VRESREAD              resolution of voltage readings (V)
#    .IRESREAD              resolution of current readings (A)
#    .VOFFSETMAX            max. offset of V read vs set
#    .MAXSETTLETIME         max. time allowed to attain stable output values
#                               (will complain if output not stable after this time) (s)
#    .READIDLETIME          idle time between readings for checking if output values of newly set
#                               voltage/current values are at set point, or when checking if
#                               consecutive measurement readings are consistent (s)
#    .V_SET_CALPOLY         tuple of polynomial coefficients ai, such that for a desired voltage output x the correct
#                               setpoint y is given by y(x) = a0 + a1*x + a2*x^2 + ...
#    .V_READ_CALPOLY        tuple of polynomial coefficients ai, such that for a given voltage reading
#                               the true input voltage y is given by y(x) = a0 + a1*x + a2*x^2 + ...
#    .I_SET_CALPOLY         same as I_SET_CALPOLY, but for I setting
#    .I_READ_CALPOLY        same as V_READ_CALPOLY, but for I reading
#    .TEST_VSTART           start value for test (V)
#    .TEST_VEND             end value for test (V)
#    .TEST_ILIMIT           current limit for test (A)
#    .TEST_PLIMIT           power limit for test (W)
#    .TEST_VIDLE            voltage limit for idle conditions during test (V)
#    .TEST_IIDLE            current limit for idle conditions during test (A)
#    .TEST_N                number of test voltage steps (V)
#    .TEST_POLARITY         polarity of connections to the PSU (1 or -1)



class PSUCOMPOSITE:

    # def __init__(self, *args):
    #     self.physical_psu_objects_list = []  # list of physical psu s
    #     for count, p in enumerate(args):
    #         self.physical_psu_objects_list[count] = p

    instancecount = 0
    def __init__(self, psuslist):

        PSUCOMPOSITE.instancecount += 1
        self.name = "Composite PSU " + str(PSUCOMPOSITE.instancecount)
        print(psuslist)
        self._physical_psus_list = psuslist  # list of physical psu s

        self.VMIN = sum([i.VMIN for i in self._physical_psus_list])
        self.VMAX = sum([i.VMAX for i in self._physical_psus_list])
        self.IMAX = min([i.IMAX for i in self._physical_psus_list])
        self.IRESSET = max([i.IRESSET for i in self._physical_psus_list])
        if self.IRESSET < 1:
            self.IRESSETCNT = len(str(self.IRESSET).split(".")[1])
        else:
            self.IRESSETCNT = 0
        self.VRESSET = min([i.VRESSET for i in self._physical_psus_list])
        if self.VRESSET < 1:
            self.VRESSETCNT = len(str(self.VRESSET).split(".")[1])
        else:
            self.VRESSETCNT = 0
        self.VRESSETCNTMAX = max([i.VRESSETCNT for i in self._physical_psus_list])    # max voltage resolution of physical psu s
        self.INDEX_OF_PPSU_VRESSETCNTMAX = ([i.VRESSETCNT for i in self._physical_psus_list].index(self.VRESSETCNTMAX))   # physical psu with max resolution
        self.VMAXLIST = [i.VMAX for i in self._physical_psus_list]
        print(self.VMAXLIST)

        self._PCT_DISTRIBUTION = [i * 100 / sum(self.VMAXLIST) for i in self.VMAXLIST]

        self.IRESSETCNTMAX = min([i.IRESSETCNT for i in self._physical_psus_list])  # min current resolution of physical psu s
        self.PMAX = sum([i.PMAX for i in self._physical_psus_list])
        # self.VOFFSETMAX = sum([i.VOFFSETMAX for i in self.physical_psu_objects_list])
        # self.IOFFSETMAX = max([i.IMAXwidget for i in self.physical_psu_objects_list])
        # self.MAXSETTLETIME = max([i.MAXSETTLETIME for i in self.physical_psu_objects_list])
        # self.READIDLETIME = self.MAXSETTLETIME / 50

        self.polarity = True

        logger.info('VRESSETCNTMAX = ' + str(self.VRESSETCNTMAX) + '\n' +
                    'self.VMIN = ' + str(self.VMIN) + '\n' +
                    'VMAX = ' + str(self.VMAX) + '\n' +
                    'IMAXwidget = ' + str(self.IMAX) + '\n' +
                    'PMAX = ' + str(self.PMAX) + '\n')


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

    def Vstartconditions(self, value):
        if value > self.VENDwidget.widgetSpinbox.value():
            self.VENDwidget.widgetSpinbox.setValue(self.VSTARTwidget.widgetSpinbox.value())

    def Vendconditions(self, value):
        if value < self.VSTARTwidget.widgetSpinbox.value():
            self.VSTARTwidget.widgetSpinbox.setValue(self.VENDwidget.widgetSpinbox.value())

    def disablespinbxs(self, disable):
        for widget in self._PSUlayout.parentWidget().findChildren(QDoubleSpinBox):
            widget.setDisabled(disable)

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


    def setvoltage(self, voltage):
        if (voltage <= self.VMAX) and (voltage >= self.VMIN):
            _voltage_list = [i * voltage for i in self._PCT_DISTRIBUTION]    # split voltage according to max voltage of each physical psu
            fractional = 0
            for count, v in enumerate(_voltage_list):
                if count == self.INDEX_OF_PPSU_VRESSETCNTMAX:   # skip the psu with the highest resolution
                    pass
                else:
                    fractional += (v % 1)                   # sum all fractional parts of voltages except the voltage of the psu with the highest resolution
                    _voltage_list[count] = v - fractional    # remove the fractional part of the set voltage of each ppsu except of the psu with the highest resolution
            _voltage_list[self.INDEX_OF_PPSU_VRESSETCNTMAX] = _voltage_list[self.INDEX_OF_PPSU_VRESSETCNTMAX] + fractional    # add the sum of the fractional parts to the ppsu with the highest resolutio
            _set_voltage = tuple(zip(self._physical_psus_list, _voltage_list))

            # set the voltage of each physical PSU:
            for p, v in _set_voltage:
                p.voltage(v)
            return 0
        else:
            logging.warning("voltage setting out of bounds "
                            + self. VMAX + " max / " + self.VMIN + " min ")
            return 1

    def setcurrent(self, current):
        _current = round(current, self.IRESSETCNTMAX)
        if (current <= self.IMAX) and (current >= self.IMIN):
            for p in self._physical_psus_list:
                p.current(_current)
            return 0
        else:
            logging.warning("current setting out of bounds "
                            + self.IMAX + " max / " + self.IMIN + " min ")
            return 1

    def turnoff(self):
        for p in self._physical_psus_list:
            p.output(False)
            p.voltage(self.VMIN)
            p.current(0.0)

    def turnon(self):
        for p in self._physical_psus_list:
            p.output(True)

    def read(self, n=1):
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
            for p in self._physical_psus_list:
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
