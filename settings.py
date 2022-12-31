from PyQt5.QtCore import QSettings
from constants import *
import curvetracePSU
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def getkey(value):
    for psu, PSUclass in physicalpsusClasses.items():
        if PSUclass.__name__ == value:
            return psu
    else:
        return EmptyPSU


class StartupSettings:
    def __init__(self, psudict):
        self._settings = QSettings()
        self.PSUdict = psudict

    def readsettings(self):
        try:
            _vgs_setting = self._settings.value("Vgs PSU")
            _vds_setting = self._settings.value("Vds PSU")

            _vgsport = self._settings.value("Vgs PSU port")
            _vdsport = self._settings.value("Vds PSU port")

            self.PSUdict["Vgs PSU"] = curvetracePSU.createPSUclass(physicalpsusClasses[_vgs_setting])(_vgsport)
            self.PSUdict["Vgs PSU"].VSTARTwidget.widgetSpinbox.setValue(float(self._settings.value("Vgs PSU start")))
            self.PSUdict["Vgs PSU"].VENDwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU end")))
            self.PSUdict["Vgs PSU"].STEPwidget.widgetSpinbox.setValue(float(self._settings.value("Vgs PSU step")))
            self.PSUdict["Vgs PSU"].IMAXwidget.widgetSpinbox.setValue(int(self._settings.value("Vds PSU Imax")))

            self.PSUdict["Vds PSU"] = curvetracePSU.createPSUclass(physicalpsusClasses[_vds_setting])(_vdsport)
            self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU start")))
            self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU end")))
            self.PSUdict["Vds PSU"].STEPwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU step")))
            self.PSUdict["Vds PSU"].IMAXwidget.widgetSpinbox.setValue(int(self._settings.value("Vds PSU Imax")))

        except (KeyError, TypeError) as e:
            logger.exception("Key error in applysettings method of StartupSettings class")
            print(e)
            self.PSUdict["Vgs PSU"] = curvetracePSU.createPSUclass(EmptyPSU)()
            self.PSUdict["Vds PSU"] = curvetracePSU.createPSUclass(EmptyPSU)()

    def savesettings(self):
        print(self.PSUdict["Vds PSU"].__class__.__bases__)[:-1]
        return
        vgs_psu_class_name = list(i.__name__ for i in self.PSUdict["Vgs PSU"].__class__.__bases__)[:-1]
        vds_psu_class_name = list(i.__name__ for i in self.PSUdict["Vds PSU"].__class__.__bases__)[:-1]

        self._settings.setValue("Vgs PSU", getkey(*vgs_psu_class_name))
        self._settings.setValue("Vds PSU", getkey(*vds_psu_class_name))
        _vgsport = self.PSUdict["Vgs PSU"].port
        _vdsport = self.PSUdict["Vds PSU"].port

        self._settings.setValue("Vgs PSU port", _vgsport)
        self._settings.setValue("Vgs PSU start", self.PSUdict["Vgs PSU"].VSTARTwidget.widgetSpinbox.value())
        self._settings.setValue("Vds PSU end", self.PSUdict["Vgs PSU"].VENDwidget.widgetSpinbox.value())
        self._settings.setValue("Vgs PSU step", self.PSUdict["Vgs PSU"].STEPwidget.widgetSpinbox.value())
        self._settings.setValue("Vgs PSU Imax", self.PSUdict["Vgs PSU"].IMAXwidget.widgetSpinbox.value())

        self._settings.setValue("Vds PSU port", _vdsport)
        self._settings.setValue("Vds PSU start", self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.value())
        self._settings.setValue("Vgs PSU end", self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.value())
        self._settings.setValue("Vds PSU step", self.PSUdict["Vds PSU"].STEPwidget.widgetSpinbox.value())
        self._settings.setValue("Vds PSU Imax", self.PSUdict["Vds PSU"].IMAXwidget.widgetSpinbox.value())



