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
        print("key not found")


class StartupSettings:
    def __init__(self, psudict):
        self._settings = QSettings()
        self.PSUdict = psudict

    def setpsus(self):
        try:
            _vgs_setting = self._settings.value("Vs PSU")
            _vds_setting = self._settings.value("Vds PSU")

            _vgsport = self._settings.value("Vgs PSU port")
            _vdsport = self._settings.value("Vds PSU port")
            self.PSUdict["Vgs PSU"] = curvetracePSU.createPSUclass(physicalpsusClasses[_vgs_setting])(_vgsport)
            self.PSUdict["Vds PSU"] = curvetracePSU.createPSUclass(physicalpsusClasses[_vds_setting])(_vdsport)
        except KeyError:
            logger.exception("Key error in setpsus method of StartupSettings class")
            print("exception")
            self.PSUdict["Vgs PSU"] = curvetracePSU.createPSUclass(EmptyPSU)()
            self.PSUdict["Vds PSU"] = curvetracePSU.createPSUclass(EmptyPSU)()

    def savesettings(self):
        vgs_psu_class_name = list(i.__name__ for i in self.PSUdict["Vgs PSU"].__class__.__bases__)[:-1]
        vds_psu_class_name = list(i.__name__ for i in self.PSUdict["Vds PSU"].__class__.__bases__)[:-1]

        self._settings.setValue("Vgs PSU", getkey(*vgs_psu_class_name))
        self._settings.setValue("Vds PSU", getkey(*vds_psu_class_name))
        _vgsport = self.PSUdict["Vgs PSU"].port
        _vdsport = self.PSUdict["Vds PSU"].port

        self._settings.setValue("Vgs PSU port", _vgsport)
        self._settings.setValue("Vds PSU port", _vdsport)
