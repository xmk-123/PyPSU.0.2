import serial
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QSettings
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMainWindow, QListWidget, QRadioButton, \
    QMessageBox, QLabel, QToolButton, QButtonGroup
import logging
import serial.tools.list_ports

from serial import SerialException

from VirtualPSU import VirtualPSU
from constants import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

AvailablePSUs = {}
usedports = []


def getkey(psu_class):
    for key, PSUclass in physicalpsusClasses.items():
        if PSUclass == psu_class:
            return key
        # else:
        #     return "EmptyPSU"


class PsuInitWindow(QMainWindow):

    Vgspolaritychanged = pyqtSignal(bool)
    Vdspolaritychanged = pyqtSignal(bool)
    updateMainWindow = pyqtSignal(bool)

    def __init__(self, PSUdict):
        super().__init__()

        self.PSUdict = PSUdict
        self._settings = QSettings()
        #self._settings.clear()

        self.window = QWidget()
        self.setWindowTitle(" Setup PSU")
        _INITlayout = QVBoxLayout()
        self.setCentralWidget(self.window)
        self.window.setLayout(_INITlayout)
# *************** PSUs list - Ports list

        _1sthorizlayout = QHBoxLayout()

        _psusLayout = QVBoxLayout()
        self.PsusLabel = QLabel("PSUs list")
        self.PsusLabel.setMinimumSize(150, 50)
        _psusLayout.addWidget(self.PsusLabel)

        self.PSUsListWidget = QListWidget()
        self.PSUsListWidget.addItems([v for v in physicalpsusClasses.keys() if v != "Empty PSU"])
        self.PSUsListWidget.setMinimumSize(250, 35)
        self.PSUsListWidget.adjustSize()
        self.PSUsListWidget.currentItemChanged.connect(lambda p: self.connect_physical_PSU_button.setText("Init\n %s PSU" % p.text()))
        _psusLayout.addWidget(self.PSUsListWidget)
        _1sthorizlayout.addLayout(_psusLayout)

        _portsLayout = QVBoxLayout()
        self.PortsLabel = QLabel("Ports list")
        self.PortsLabel.setMinimumSize(150, 50)
        _portsLayout.addWidget(self.PortsLabel)

        self.PortsListWidget = QListWidget()
        self.PortsListWidget.addItems(self.serial_ports())
        self.PortsListWidget.setMinimumSize(250, 35)
        self.PortsListWidget.adjustSize()
        _portsLayout.addWidget(self.PortsListWidget)
        _1sthorizlayout.addLayout(_portsLayout)

        _INITlayout.addLayout(_1sthorizlayout)
# *************** connect physical psu - Update ports  buttons

        _2ndhorizlayout = QHBoxLayout()

        self.connect_physical_PSU_button = QPushButton("Connect PSU")
        self.connect_physical_PSU_button.clicked.connect(self.checkandconnect_physical_psu)
        _2ndhorizlayout.addWidget(self.connect_physical_PSU_button)

        self.updateportsbutton = QPushButton("Update\nPorts")
        self.updateportsbutton.clicked.connect(self.refreshports)
        _2ndhorizlayout.addWidget(self.updateportsbutton)
        _INITlayout.addLayout(_2ndhorizlayout)

# *************** PSUs used by Vgs PSU
        _3rddhorizlayout = QHBoxLayout()

        _VgsPSUlayout = QVBoxLayout()

        self.VgsPSULabel = QLabel("In use by Vgs PSU")
        self.VgsPSULabel.setMinimumSize(150, 50)
        _VgsPSUlayout.addWidget(self.VgsPSULabel)

        self.VgsPSUsListWidget = QListWidget()
        self.VgsPSUsListWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.VgsPSUsListWidget.setMinimumSize(250, 35)
        self.VgsPSUsListWidget.adjustSize()
        #self.VgsPSUsListWidget.addItems(AvailablePSUs.keys())
        _VgsPSUlayout.addWidget(self.VgsPSUsListWidget)

        _VgsPSUlayout.addStretch()

        # *************** Polarity

        self._VgsRadioButtonGrp = QButtonGroup()
        _polarityVgsPSUlayout = QVBoxLayout()
        VgsPolarity = QRadioButton("Source negative")
        _VgsPSUlayout.addWidget(VgsPolarity)
        VgsPolarity.setChecked(self.PSUdict["Vgs PSU"].polarity)
        VgsPolarity.toggled.connect(lambda s: self.Vgspolaritychanged.emit(s))
        VgsPolarity2 = QRadioButton("Source positive")
        _VgsPSUlayout.addWidget(VgsPolarity2)
        VgsPolarity2.setChecked(not self.PSUdict["Vgs PSU"].polarity)

        self._VgsRadioButtonGrp.addButton(VgsPolarity)
        self._VgsRadioButtonGrp.addButton(VgsPolarity2)

        _VgsPSUlayout.addLayout(_polarityVgsPSUlayout)
        _3rddhorizlayout.addLayout(_VgsPSUlayout)

        _VgsPSUlayout.addStretch()
        # *************** add/remove ready PSU button

        addremoveVgsPSUbuttonlayout = QVBoxLayout()
        addremoveVgsPSUbuttonlayout.addStretch()
        self.addToVgsPSUbutton = QToolButton()
        self.addToVgsPSUbutton.setArrowType(QtCore.Qt.LeftArrow)
        self.addToVgsPSUbutton.clicked.connect(lambda x: self.add_to_psu_list_widget(self.VgsPSUsListWidget))
        addremoveVgsPSUbuttonlayout.addWidget(self.addToVgsPSUbutton)

        self.removefromVgsPSUbutton = QToolButton()
        self.removefromVgsPSUbutton.setArrowType(QtCore.Qt.RightArrow)
        self.removefromVgsPSUbutton.clicked.connect(lambda x: self.remove_from_psu_list_widget(self.VgsPSUsListWidget))
        addremoveVgsPSUbuttonlayout.addWidget(self.removefromVgsPSUbutton)
        addremoveVgsPSUbuttonlayout.addStretch()

        _3rddhorizlayout.addLayout(addremoveVgsPSUbuttonlayout)

# *************** Available PSUs

        _initPSUlayout = QVBoxLayout()

        self.AvailablePsusLabel = QLabel("Available PSUs")
        self.AvailablePsusLabel.setMinimumSize(150, 50)
        _initPSUlayout.addWidget(self.AvailablePsusLabel)

        self.AvailablePSUsWidget = QListWidget()
        self.AvailablePSUsWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.AvailablePSUsWidget.setMinimumSize(250, 35)
        self.AvailablePSUsWidget.adjustSize()
        #self.AvailablePSUsWidget.addItems(AvailablePSUs.keys())
        _initPSUlayout.addWidget(self.AvailablePSUsWidget)

        # items = [self.PSUsListWidget.item(x).text() for x in range(self.PSUsListWidget.count())]
        # self.CurrentRow = items.index(str(self.psu.name))
        # self.PSUsListWidget.setCurrentRow(self.CurrentRow)
        # items = [self.PortsListWidget.item(x).text() for x in range(self.PortsListWidget.count())]
        # self.CurrentRow = items.index(str(self.port))
        # self.PortsListWidget.setCurrentRow(self.CurrentRow)

        # items = [self.AvailablePSUsWidget.item(x).text() for x in range(self.PortsListWidget.count())]
        # self.CurrentRow = items.index(str(self.psu.name))
        # self.PortsListWidget.setCurrentRow(self.CurrentRow)

        _initPSUlayout.addStretch()

        # *************** Initialize button - delete button - exit button

        self.InitButton = QPushButton('Create')
        self.InitButton.setMinimumSize(150, 65)
        self.InitButton.pressed.connect(self.create_virtual_psus)
        _initPSUlayout.addWidget(self.InitButton)

        self.DisconnectPhysicalPsuButton = QPushButton('Disconnect')
        self.DisconnectPhysicalPsuButton.setMinimumSize(150, 65)
        self.DisconnectPhysicalPsuButton.pressed.connect(self.disconnect_physical_psu)
        _initPSUlayout.addWidget(self.DisconnectPhysicalPsuButton)

        self.ExitButton = QPushButton('Exit')
        self.ExitButton.setMinimumSize(150, 65)
        self.ExitButton.pressed.connect(self.close)
        _initPSUlayout.addWidget(self.ExitButton)

        _3rddhorizlayout.addLayout(_initPSUlayout)

        # *************** add/remove ready PSU button

        addremoveVdsPSUbuttonlayout = QVBoxLayout()

        addremoveVdsPSUbuttonlayout.addStretch()
        self.removefromVdsPSUbutton = QToolButton()
        self.removefromVdsPSUbutton.setArrowType(QtCore.Qt.RightArrow)
        self.removefromVdsPSUbutton.clicked.connect(lambda x: self.add_to_psu_list_widget(self.VdsPSUsListWidget))
        addremoveVdsPSUbuttonlayout.addWidget(self.removefromVdsPSUbutton)

        self.addToVdsPSUbutton = QToolButton()
        self.addToVdsPSUbutton.setArrowType(QtCore.Qt.LeftArrow)
        self.addToVdsPSUbutton.clicked.connect(lambda x: self.remove_from_psu_list_widget(self.VdsPSUsListWidget))
        addremoveVdsPSUbuttonlayout.addWidget(self.addToVdsPSUbutton)

        addremoveVdsPSUbuttonlayout.addStretch()
        _3rddhorizlayout.addLayout(addremoveVdsPSUbuttonlayout)

# *************** PSUs used by Vds PSU

        _VdsPSUlayout = QVBoxLayout()

        self.VdsPSUsListLabel = QLabel("In use by Vds PSU")
        self.VdsPSUsListLabel.setMinimumSize(150, 50)
        _VdsPSUlayout.addWidget(self.VdsPSUsListLabel)

        self.VdsPSUsListWidget = QListWidget()
        self.VdsPSUsListWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.VdsPSUsListWidget.setMinimumSize(250, 35)
        self.VdsPSUsListWidget.adjustSize()
        #self.VdsPSUsListWidget.addItems(AvailablePSUs.keys())
        _VdsPSUlayout.addWidget(self.VdsPSUsListWidget)

        _VdsPSUlayout.addStretch()
        # *************** Polarity

        self._VdsRadioButtonGrp = QButtonGroup()
        _polarityVdsPSUlayout = QVBoxLayout()
        VdsPolarity = QRadioButton("Source negative")
        _polarityVdsPSUlayout.addWidget(VdsPolarity)
        VdsPolarity.setChecked(self.PSUdict["Vds PSU"].polarity)
        VdsPolarity.toggled.connect(lambda s: self.Vdspolaritychanged.emit(s))
        VdsPolarity2 = QRadioButton("Source positive")
        _polarityVdsPSUlayout.addWidget(VdsPolarity2)
        VdsPolarity2.setChecked(not self.PSUdict["Vds PSU"].polarity)

        self._VdsRadioButtonGrp.addButton(VdsPolarity)
        self._VdsRadioButtonGrp.addButton(VdsPolarity2)

        _VdsPSUlayout.addLayout(_polarityVdsPSUlayout)

        _VdsPSUlayout.addStretch()

        _3rddhorizlayout.addLayout(_VdsPSUlayout)

        _INITlayout.addLayout(_3rddhorizlayout)
        #self.applysettings()

    def add_to_psu_list_widget(self, psulistwidget):
        for i in self.AvailablePSUsWidget.selectedItems():
            psulistwidget.addItem(i.text())
            self.AvailablePSUsWidget.takeItem(self.AvailablePSUsWidget.row(i))

    def remove_from_psu_list_widget(self, psulistwidget):
        for i in psulistwidget.selectedItems():
            psulistwidget.takeItem(psulistwidget.row(i))
            self.AvailablePSUsWidget.addItem(i.text())

    def serial_ports(self):
        result = ([comport.device for comport in serial.tools.list_ports.comports()])
        result.append("TestPort1")
        result.append("TestPort2")
        for p in usedports:
            if p in result:
                result.remove(p)
        return result

    def refreshports(self):
        self.PortsListWidget.clear()
        self.PortsListWidget.addItems(self.serial_ports())

    def checkandconnect_physical_psu(self):
        if len(self.PSUsListWidget.selectedItems()) > 0 and len(self.PortsListWidget.selectedItems()) > 0:
            ready_psu_name = self.connect_physical_psu(physicalpsusClasses[self.PSUsListWidget.currentItem().text()],
                                                       self.PortsListWidget.currentItem().text())
            self.AvailablePSUsWidget.addItem(ready_psu_name)
            self.PortsListWidget.takeItem(self.PortsListWidget.currentRow())
            self.refreshports()

    def connect_physical_psu(self, _psu_class, _selected_port):
        try:
            physical_psu_instance = _psu_class(_selected_port)
            ready_psu_name = str(physical_psu_instance.name + " / " + physical_psu_instance.MODEL + "\n   at port: " + physical_psu_instance.port)
            physical_psu_instance.name = ready_psu_name
            AvailablePSUs.update({ready_psu_name: physical_psu_instance})
            physical_psu_instance = None
            usedports.append(_selected_port)
            return ready_psu_name

        except SerialException as e:
            logger.warning("error\n %s" % e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(str(e))
            msg.setStandardButtons(QMessageBox.Close)
            msg.exec()

    def disconnect_physical_psu(self):
        for selected in self.AvailablePSUsWidget.selectedItems():
            if AvailablePSUs[selected.text()] in self.PSUdict["Vgs PSU"].physical_psu_objects_list or \
               AvailablePSUs[selected.text()] in self.PSUdict["Vds PSU"].physical_psu_objects_list:
                self.create_virtual_psus()
            usedports.remove(AvailablePSUs[selected.text()].port)
            self.refreshports()
            del AvailablePSUs[selected.text()]
            self.AvailablePSUsWidget.takeItem(self.AvailablePSUsWidget.row(selected))

    def create_virtual_psus(self):

        _VgsPSUsSelected = [str(self.VgsPSUsListWidget.item(i).text()) for i in range(self.VgsPSUsListWidget.count())]
        _VdsPSUsSelected = [str(self.VdsPSUsListWidget.item(i).text()) for i in range(self.VdsPSUsListWidget.count())]

        for names, key in [(_VgsPSUsSelected, "Vgs PSU"), (_VdsPSUsSelected, "Vds PSU")]:

            match len(names):
                case 0:
                    self.PSUdict[key] = VirtualPSU([EmptyPSU()])
                case 1:
                    self.PSUdict[key] = VirtualPSU([AvailablePSUs[names[0]]])
                case _ if len(names) > 1:
                    self.PSUdict[key] = VirtualPSU([AvailablePSUs[name] for name in names])
                case _:
                    return
        self.updateMainWindow.emit(True)

    def applysettings(self):
        try:
            _vgs_settings = self._settings.value("Vgs physical PSU objects")
            _vds_settings = self._settings.value("Vds physical PSU objects")

            if _vgs_settings is not None and _vds_settings is not None:
                for psu_class, port in _vgs_settings:
                    ready_psu_name = self.connect_physical_psu(psu_class, port)
                    self.VgsPSUsListWidget.addItem(ready_psu_name)

                for psu_class, port in _vds_settings:
                    ready_psu_name = self.connect_physical_psu(psu_class, port)
                    self.VdsPSUsListWidget.addItem(ready_psu_name)

                self.PSUdict["Vgs PSU"].VSTARTwidget.widgetSpinbox.setValue(float(self._settings.value("Vgs PSU start")))
                self.PSUdict["Vgs PSU"].VENDwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU end")))
                self.PSUdict["Vgs PSU"].STEPwidget.widgetSpinbox.setValue(float(self._settings.value("Vgs PSU step")))
                self.PSUdict["Vgs PSU"].IMAXwidget.widgetSpinbox.setValue(int(self._settings.value("Vds PSU Imax")))

                self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU start")))
                self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU end")))
                self.PSUdict["Vds PSU"].STEPwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU step")))
                self.PSUdict["Vds PSU"].IMAXwidget.widgetSpinbox.setValue(int(self._settings.value("Vds PSU Imax")))
            else:
                self.PSUdict["Vgs PSU"] = VirtualPSU([EmptyPSU()])
                self.PSUdict["Vds PSU"] = VirtualPSU([EmptyPSU()])

        except (KeyError, TypeError) as e:
            logger.exception("Key error in applysettings method of StartupSettings class")
            self.PSUdict["Vgs PSU"] = VirtualPSU([EmptyPSU()])
            self.PSUdict["Vds PSU"] = VirtualPSU([EmptyPSU()])

    def savesettings(self):

        vgs_psu_class_names_and_ports = []
        vds_psu_class_names_and_ports = []

        for psu_object in self.PSUdict["Vgs PSU"].physical_psu_objects_list:
            vgs_psu_class_names_and_ports.append((getkey(psu_object.__class__), psu_object.port))

        for psu_object in self.PSUdict["Vds PSU"].physical_psu_objects_list:
            vgs_psu_class_names_and_ports.append((getkey(psu_object.__class__), psu_object.port))

        self._settings.setValue("Vgs physical PSU objects", vgs_psu_class_names_and_ports)
        self._settings.setValue("Vgs PSU start", self.PSUdict["Vgs PSU"].VSTARTwidget.widgetSpinbox.value())
        self._settings.setValue("Vds PSU end", self.PSUdict["Vgs PSU"].VENDwidget.widgetSpinbox.value())
        self._settings.setValue("Vgs PSU step", self.PSUdict["Vgs PSU"].STEPwidget.widgetSpinbox.value())
        self._settings.setValue("Vgs PSU Imax", self.PSUdict["Vgs PSU"].IMAXwidget.widgetSpinbox.value())

        self._settings.setValue("Vds physical PSU objects", vds_psu_class_names_and_ports)
        self._settings.setValue("Vds PSU start", self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.value())
        self._settings.setValue("Vgs PSU end", self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.value())
        self._settings.setValue("Vds PSU step", self.PSUdict["Vds PSU"].STEPwidget.widgetSpinbox.value())
        self._settings.setValue("Vds PSU Imax", self.PSUdict["Vds PSU"].IMAXwidget.widgetSpinbox.value())
