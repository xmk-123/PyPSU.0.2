import time
from io import StringIO
import sys
import serial
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QSettings
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMainWindow, QListWidget, QRadioButton, \
    QMessageBox, QLabel, QToolButton, QButtonGroup, QFrame, QSizePolicy, QAbstractItemView
import logging
import serial.tools.list_ports

from VirtualPSU import VirtualPSU
from constants import *

from PyQt5.QtCore import Qt

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

    def __init__(self, psudict):
        super().__init__()

        self.PSUdict = psudict

        self._settings = QSettings()
        # self._settings.clear()

        self.window = QWidget()
        self.setWindowTitle(" Setup PSU")
        _INITlayout = QVBoxLayout()
        self.setCentralWidget(self.window)
        self.window.setLayout(_INITlayout)
# *************** PSUs list - Ports list - thermometer sensor

        _1sthorizlayout = QHBoxLayout()

        _psusLayout = QVBoxLayout()
        self.PsusLabel = QLabel("PSUs list")
        self.PsusLabel.setMinimumSize(150, 50)
        _psusLayout.addWidget(self.PsusLabel)

        self.PSUsListWidget = QListWidget()
        self.PSUsListWidget.addItems([v for v in physicalpsusClasses.keys() if v != "Empty PSU"])
        self.PSUsListWidget.setMinimumSize(250, 35)
        self.PSUsListWidget.adjustSize()
        self.PSUsListWidget.currentItemChanged.connect(
            lambda p: self.connect_physical_PSU_button.setText("Init\n %s PSU" % p.text()))
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

        _SensorLayout = QVBoxLayout()
        self.SensorLabel = QLabel("Sensors list")
        self.SensorLabel.setMinimumSize(150, 50)
        _SensorLayout.addWidget(self.SensorLabel)

        self.SensorListWidget = QListWidget()
        self.SensorListWidget.addItems(([t for t in temperatureSensorsClasses.keys()]))
        self.SensorListWidget.setMinimumSize(250, 35)
        self.SensorListWidget.adjustSize()
        _SensorLayout.addWidget(self.SensorListWidget)
        _1sthorizlayout.addLayout(_SensorLayout)

        _INITlayout.addLayout(_1sthorizlayout)
# *************** connect physical psu - Update ports  buttons

        _2ndhorizlayout = QHBoxLayout()

        self.connect_physical_PSU_button = QPushButton("Connect PSU")
        self.connect_physical_PSU_button.clicked.connect(self.checkandconnect_physical_psu)
        _2ndhorizlayout.addWidget(self.connect_physical_PSU_button)

        self.updateportsbutton = QPushButton("Update\nPorts")
        self.updateportsbutton.clicked.connect(self.refreshports)
        _2ndhorizlayout.addWidget(self.updateportsbutton)

        self.connect_sensor_button = QPushButton("Connect\nsensor")
        self.connect_sensor_button.clicked.connect(self.checkandconnect_sensor)
        _2ndhorizlayout.addWidget(self.connect_sensor_button)
        _INITlayout.addLayout(_2ndhorizlayout)

        separator_1 = QFrame()
        separator_1.setFrameShape(QFrame.HLine)
        separator_1.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator_1.setLineWidth(5)

        separator_2 = QFrame()
        separator_2.setFrameShape(QFrame.HLine)
        separator_2.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator_2.setLineWidth(5)

        _INITlayout.addWidget(separator_1)
        _INITlayout.addWidget(separator_2)

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
        self.VgsPSUsListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.VgsPSUsListWidget.setDefaultDropAction(Qt.MoveAction)
        _VgsPSUlayout.addWidget(self.VgsPSUsListWidget)

        _VgsPSUlayout.addStretch()

        # *************** test PSU -- Polarity radio buttons

        self.TestVgsButton = QPushButton('Test')
        self.TestVgsButton.setMinimumSize(150, 65)
        self.TestVgsButton.pressed.connect(lambda: self.test_psu("Vgs PSU"))
        _VgsPSUlayout.addWidget(self.TestVgsButton)

        self._VgsRadioButtonGrp = QButtonGroup()
        _polarityVgsPSUlayout = QVBoxLayout()
        vgs_polarity = QRadioButton("Source negative")
        _VgsPSUlayout.addWidget(vgs_polarity)
        vgs_polarity.setChecked(self.PSUdict["Vgs PSU"].polarity)
        vgs_polarity.toggled.connect(lambda s: self.Vgspolaritychanged.emit(s))
        vgs_polarity2 = QRadioButton("Source positive")
        _VgsPSUlayout.addWidget(vgs_polarity2)
        vgs_polarity2.setChecked(not self.PSUdict["Vgs PSU"].polarity)

        self._VgsRadioButtonGrp.addButton(vgs_polarity)
        self._VgsRadioButtonGrp.addButton(vgs_polarity2)

        _VgsPSUlayout.addLayout(_polarityVgsPSUlayout)
        _3rddhorizlayout.addLayout(_VgsPSUlayout)

        _VgsPSUlayout.addStretch()

# *************** Available PSUs

        _initPSUlayout = QVBoxLayout()

        self.AvailablePsusLabel = QLabel("Available PSUs")
        self.AvailablePsusLabel.setMinimumSize(150, 50)
        _initPSUlayout.addWidget(self.AvailablePsusLabel)

        self.AvailablePSUsWidget = QListWidget()
        self.AvailablePSUsWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.AvailablePSUsWidget.setMinimumSize(250, 35)
        self.AvailablePSUsWidget.adjustSize()
        self.AvailablePSUsWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.AvailablePSUsWidget.setDefaultDropAction(Qt.MoveAction)
        _initPSUlayout.addWidget(self.AvailablePSUsWidget)

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
        self.ExitButton.pressed.connect(self.hide)
        _initPSUlayout.addWidget(self.ExitButton)

        _3rddhorizlayout.addLayout(_initPSUlayout)

# *************** PSUs used by Vds PSU

        _VdsPSUlayout = QVBoxLayout()

        self.VdsPSUsListLabel = QLabel("In use by Vds PSU")
        self.VdsPSUsListLabel.setMinimumSize(150, 50)
        _VdsPSUlayout.addWidget(self.VdsPSUsListLabel)

        self.VdsPSUsListWidget = QListWidget()
        self.VdsPSUsListWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.VdsPSUsListWidget.setMinimumSize(250, 35)
        self.VdsPSUsListWidget.adjustSize()
        self.VdsPSUsListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.VdsPSUsListWidget.setDefaultDropAction(Qt.MoveAction)
        _VdsPSUlayout.addWidget(self.VdsPSUsListWidget)

        _VdsPSUlayout.addStretch()
        # ***************  test PSU --Polarity

        self.TestVdsButton = QPushButton('Test')
        self.TestVdsButton.setMinimumSize(150, 65)
        self.TestVdsButton.pressed.connect(lambda: self.test_psu("Vds PSU"))
        _VdsPSUlayout.addWidget(self.TestVdsButton)

        self._VdsRadioButtonGrp = QButtonGroup()
        _polarityVdsPSUlayout = QVBoxLayout()
        vds_polarity = QRadioButton("Source negative")
        _polarityVdsPSUlayout.addWidget(vds_polarity)
        vds_polarity.setChecked(self.PSUdict["Vds PSU"].polarity)
        vds_polarity.toggled.connect(lambda s: self.Vdspolaritychanged.emit(s))
        vds_polarity2 = QRadioButton("Source positive")
        _polarityVdsPSUlayout.addWidget(vds_polarity2)
        vds_polarity2.setChecked(not self.PSUdict["Vds PSU"].polarity)

        self._VdsRadioButtonGrp.addButton(vds_polarity)
        self._VdsRadioButtonGrp.addButton(vds_polarity2)

        _VdsPSUlayout.addLayout(_polarityVdsPSUlayout)

        _VdsPSUlayout.addStretch()

        _3rddhorizlayout.addLayout(_VdsPSUlayout)

        # *************** PSUs used by Heater

        separator_3 = QFrame()
        separator_3.setFrameShape(QFrame.VLine)
        separator_3.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator_3.setLineWidth(5)

        _3rddhorizlayout.addWidget(separator_3)


        _HeaterPSUlayout = QVBoxLayout()

        self.HeaterPSULabel = QLabel("In use by Heater")
        self.HeaterPSULabel.setMinimumSize(150, 50)
        _HeaterPSUlayout.addWidget(self.HeaterPSULabel)

        self.HeaterPSUsListWidget = QListWidget()
        self.HeaterPSUsListWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.HeaterPSUsListWidget.setMinimumSize(250, 35)
        self.HeaterPSUsListWidget.adjustSize()
        self.HeaterPSUsListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.HeaterPSUsListWidget.setDefaultDropAction(Qt.MoveAction)
        _HeaterPSUlayout.addWidget(self.HeaterPSUsListWidget)

        self.TestHeaterButton = QPushButton('Test')
        self.TestHeaterButton.setMinimumSize(150, 65)
        self.TestHeaterButton.pressed.connect(lambda: self.test_psu("Heater PSU"))
        _HeaterPSUlayout.addWidget(self.TestHeaterButton)

        _3rddhorizlayout.addLayout(_HeaterPSUlayout)

        _VgsPSUlayout.addStretch()

        # *************** temperature sensor connected

        _sensorConnectedlayout = QVBoxLayout()

        self.sensorConnectedLabel = QLabel("Temperature sensor")
        self.sensorConnectedLabel.setMinimumSize(150, 50)
        _sensorConnectedlayout.addWidget(self.sensorConnectedLabel)

        self.sensorConnectedPlaceholder = QLabel()
        self.sensorConnectedPlaceholder.setMinimumSize(150, 50)
        _sensorConnectedlayout.addWidget(self.sensorConnectedPlaceholder)

        self.DisconnectSensorButton = QPushButton('Disconnect sensor')
        self.DisconnectSensorButton.setMinimumSize(150, 65)
        self.DisconnectSensorButton.pressed.connect(self.disconnect_sensor)
        _sensorConnectedlayout.addWidget(self.DisconnectSensorButton)
        _sensorConnectedlayout.addStretch()

        _3rddhorizlayout.addLayout(_sensorConnectedlayout)

        _INITlayout.addLayout(_3rddhorizlayout)

    def test_psu(self, psu):
        if self.PSUdict[psu].name != "Empty PSU":
            self.PSUdict[psu].enableoutput(False)
            for i in range(2):
                for physicalpsu in self.PSUdict[psu].physical_psu_objects_list:
                    physicalpsu.setcurrent(float("1." + "9" * physicalpsu.VRESSETCNT))
                time.sleep(1)
                for physicalpsu in self.PSUdict[psu].physical_psu_objects_list:
                    physicalpsu.setcurrent(0)
                    time.sleep(1)

    def checkandconnect_sensor(self):
        if len(self.SensorListWidget.selectedItems()) == 1 and len(self.PortsListWidget.selectedItems()) == 1:
            self.connect_sensor(self.SensorListWidget.currentItem().text(), self.PortsListWidget.currentItem().text(), True)

    def connect_sensor(self, sensor_class, port, verbose=False):
        if len(self.sensorConnectedPlaceholder.text()) == 0:
            try:
                self.PSUdict["Temperature Sensor"] = temperatureSensorsClasses[sensor_class](UART_Adapter(port))
                usedports.append(port)
                self.sensorConnectedPlaceholder.setText(sensor_class + "\n at port \n" + port)
                self.refreshports()

                old_stdout = sys.stdout
                sys.stdout = mystdout = StringIO()
                self.PSUdict["Temperature Sensor"].info()
                sys.stdout = old_stdout

                if verbose:
                    self.popup_message("Temperature probe CONECTED\n" + mystdout.getvalue())

            except BaseException as e:
                self.PSUdict["Temperature Sensor"] = None
                if verbose:
                    self.popup_message(str(e))
        else:
            self.popup_message("Sensor : " + self.sensorConnectedPlaceholder.text() + "\n is already connected")

    def disconnect_sensor(self):
        if len(self.sensorConnectedPlaceholder.text()) > 0:
            usedports.remove(self.sensorConnectedPlaceholder.text().strip().split("\n")[-1])
            self.PSUdict["Temperature Sensor"] = None
            self.sensorConnectedPlaceholder.setText("")
            self.refreshports()

    def serial_ports(self):
        result = ([comport.device for comport in serial.tools.list_ports.comports()])
        result.append("Test_Vgs_Port")
        result.append("Test_Vds_Port")
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
                                                       self.PortsListWidget.currentItem().text(), True)
            self.AvailablePSUsWidget.addItem(ready_psu_name)
            self.PortsListWidget.takeItem(self.PortsListWidget.currentRow())
            self.refreshports()

    def connect_physical_psu(self, _psu_class, _selected_port, verbose=False):
        try:
            physical_psu_instance = _psu_class(_selected_port)
            ready_psu_name = str(physical_psu_instance.name + " / " + physical_psu_instance.MODEL +
                                 "\n   at port: " + physical_psu_instance.port)
            physical_psu_instance.name = ready_psu_name
            AvailablePSUs.update({ready_psu_name: physical_psu_instance})
            usedports.append(_selected_port)
            self.refreshports()
            return ready_psu_name

        except (IOError, RuntimeError) as e:
            if verbose:
                print(e)
                self.popup_message(str(e))
            else:
                raise e

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
        _HeaterPSUsSelected = [str(self.HeaterPSUsListWidget.item(i).text()) for i in range(self.HeaterPSUsListWidget.count())]

        for names, key in [(_VgsPSUsSelected, "Vgs PSU"), (_VdsPSUsSelected, "Vds PSU"), (_HeaterPSUsSelected, "Heater PSU")]:
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
            _heater_settings = self._settings.value("Heater physical PSU objects")

            for psu, settings in (("Vgs PSU", _vgs_settings), ("Vds PSU", _vds_settings), ("Heater PSU", _heater_settings)):
                if settings is None or settings[0][0] == "Empty PSU":
                    self.PSUdict[psu] = VirtualPSU([EmptyPSU()])
                else:
                    for psu_class, port in settings:
                        try:
                            ready_psu_name = self.connect_physical_psu(physicalpsusClasses[psu_class], port)
                            if psu == "Vgs PSU":
                                self.VgsPSUsListWidget.addItem(ready_psu_name)
                            elif psu == "Vds PSU":
                                self.VdsPSUsListWidget.addItem(ready_psu_name)
                            elif psu == "Heater PSU":
                                self.HeaterPSUsListWidget.addItem(ready_psu_name)
                        except IOError as e:
                            print(e)
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setInformativeText(str(e) + "\n\nWill start with EMPTY PSU\n\n"
                                                            "Press RESET to clear the stored startup settings\n\n"
                                                            "               or\n\nPress OK to continue \n")
                            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Reset)
                            response = msg.exec()
                            if response == QMessageBox.Reset:
                                self._settings.setValue(psu, "Empty PSU")    # .clear()
                            self.PSUdict[psu] = VirtualPSU([EmptyPSU()])
                    self.create_virtual_psus()

            self.PSUdict["Vgs PSU"].VSTARTwidget.widgetSpinbox.setValue(float(self._settings.value("Vgs PSU start")))
            self.PSUdict["Vgs PSU"].VENDwidget.widgetSpinbox.setValue(float(self._settings.value("Vgs PSU end")))
            self.PSUdict["Vgs PSU"].STEPwidget.widgetSpinbox.setValue(float(self._settings.value("Vgs PSU step")))
            self.PSUdict["Vgs PSU"].IMAXwidget.widgetSpinbox.setValue(int(self._settings.value("Vgs PSU Imax")))

            self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU start")))
            self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU end")))
            self.PSUdict["Vds PSU"].STEPwidget.widgetSpinbox.setValue(float(self._settings.value("Vds PSU step")))
            self.PSUdict["Vds PSU"].IMAXwidget.widgetSpinbox.setValue(int(self._settings.value("Vds PSU Imax")))

            self.PSUdict["DUT settings"].DUTMaxPSpinbox.setValue(int(self._settings.value("Pmax")))
            self.PSUdict["DUT settings"].TempSpinbox.setValue(int(self._settings.value("Temp")))

            self.connect_sensor(self._settings.value("Temperature Sensor").strip().split("\n")[0],
                                self._settings.value("Temperature Sensor").strip().split("\n")[-1])

        except(KeyError, TypeError):
            # logger.exception("Key error in applysettings method of StartupSettings class")
            self.PSUdict["Vgs PSU"] = VirtualPSU([EmptyPSU()])
            self.PSUdict["Vds PSU"] = VirtualPSU([EmptyPSU()])

    def savesettings(self):

        # self._settings.clear()

        vgs_psu_class_names_and_ports = []
        vds_psu_class_names_and_ports = []
        heater_psu_class_names_and_ports = []

        for psu_object in self.PSUdict["Vgs PSU"].physical_psu_objects_list:
            vgs_psu_class_names_and_ports.append((getkey(psu_object.__class__), psu_object.port))

        for psu_object in self.PSUdict["Vds PSU"].physical_psu_objects_list:
            vds_psu_class_names_and_ports.append((getkey(psu_object.__class__), psu_object.port))

        for psu_object in self.PSUdict["Heater PSU"].physical_psu_objects_list:
            heater_psu_class_names_and_ports.append((getkey(psu_object.__class__), psu_object.port))

        self._settings.setValue("Vgs physical PSU objects", vgs_psu_class_names_and_ports)
        self._settings.setValue("Vgs PSU start", self.PSUdict["Vgs PSU"].VSTARTwidget.widgetSpinbox.value())
        self._settings.setValue("Vgs PSU end", self.PSUdict["Vgs PSU"].VENDwidget.widgetSpinbox.value())
        self._settings.setValue("Vgs PSU step", self.PSUdict["Vgs PSU"].STEPwidget.widgetSpinbox.value())
        self._settings.setValue("Vgs PSU Imax", self.PSUdict["Vgs PSU"].IMAXwidget.widgetSpinbox.value())

        self._settings.setValue("Vds physical PSU objects", vds_psu_class_names_and_ports)
        self._settings.setValue("Vds PSU start", self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.value())
        self._settings.setValue("Vds PSU end", self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.value())
        self._settings.setValue("Vds PSU step", self.PSUdict["Vds PSU"].STEPwidget.widgetSpinbox.value())
        self._settings.setValue("Vds PSU Imax", self.PSUdict["Vds PSU"].IMAXwidget.widgetSpinbox.value())

        self._settings.setValue("Heater physical PSU objects", heater_psu_class_names_and_ports)

        self._settings.setValue("Pmax", self.PSUdict["DUT settings"].DUTMaxPSpinbox.value())
        self._settings.setValue("Temp", self.PSUdict["DUT settings"].TempSpinbox.value())

        self._settings.setValue("Temperature Sensor", (self.sensorConnectedPlaceholder.text()))

    def popup_message(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText(text)
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec()
