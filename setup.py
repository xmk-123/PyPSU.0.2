import time
from io import StringIO
import sys
import serial
from PyQt5.QtCore import pyqtSignal, QSettings, Qt, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMainWindow, QListWidget, QRadioButton, \
    QMessageBox, QLabel, QButtonGroup, QFrame, QSizePolicy, QAbstractItemView
import serial.tools.list_ports

from VirtualPSU import VirtualPSU
from constants import *

AvailablePSUs = {}
usedports = []


def getkey(psu_class):
    for key, PSUclass in physicalpsusClasses.items():
        if PSUclass == psu_class:
            return key


def popup_message(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setInformativeText(text)
    msg.setStandardButtons(QMessageBox.Close)
    msg.exec()


class PsuInitWindow(QMainWindow):

    Vgspolaritychanged = pyqtSignal(bool)
    Vdspolaritychanged = pyqtSignal(bool)
    updateMainWindow = pyqtSignal()

    def __init__(self, psudict):
        super().__init__()
        self.PSUdict = psudict
        self.settings = QSettings()

        self.window = QWidget()
        self.setWindowTitle(" Setup PSU")
        _INITlayout = QVBoxLayout()
        self.setCentralWidget(self.window)
        self.window.setLayout(_INITlayout)
# *************** PSUs list - Ports list - thermometer sensor

        _1sthorizlayout = QHBoxLayout()

        _psusLayout = QVBoxLayout()
        _PsusLabel = QLabel("PSUs list")
        _PsusLabel.setMinimumSize(150, 50)
        _psusLayout.addWidget(_PsusLabel)

        self.PSUsListWidget = QListWidget()
        self.PSUsListWidget.addItems([v for v in physicalpsusClasses.keys() if v != "Empty PSU"])
        self.PSUsListWidget.setMinimumSize(250, 35)
        self.PSUsListWidget.adjustSize()
        self.PSUsListWidget.currentItemChanged.connect(
            lambda p: _connect_physical_PSU_button.setText("Connect\n %s PSU" % p.text()))
        _psusLayout.addWidget(self.PSUsListWidget)
        _1sthorizlayout.addLayout(_psusLayout)

        _portsLayout = QVBoxLayout()
        _PortsLabel = QLabel("Ports list")
        _PortsLabel.setMinimumSize(150, 50)
        _portsLayout.addWidget(_PortsLabel)

        self.PortsListWidget = QListWidget()
        self.PortsListWidget.addItems(self.serial_ports())
        self.PortsListWidget.setMinimumSize(250, 35)
        self.PortsListWidget.adjustSize()
        _portsLayout.addWidget(self.PortsListWidget)
        _1sthorizlayout.addLayout(_portsLayout)

        _SensorLayout = QVBoxLayout()
        _SensorLabel = QLabel("Sensors list")
        _SensorLabel.setMinimumSize(150, 50)
        _SensorLayout.addWidget(_SensorLabel)

        self.SensorListWidget = QListWidget()
        self.SensorListWidget.addItems(([t for t in temperatureSensorsClasses.keys()]))
        self.SensorListWidget.setMinimumSize(250, 35)
        self.SensorListWidget.adjustSize()
        _SensorLayout.addWidget(self.SensorListWidget)
        _1sthorizlayout.addLayout(_SensorLayout)

        _INITlayout.addLayout(_1sthorizlayout)
# *************** connect physical psu - Update ports  buttons

        _2ndhorizlayout = QHBoxLayout()

        _connect_physical_PSU_button = QPushButton("Connect PSU")
        _connect_physical_PSU_button.clicked.connect(self.checkandconnect_physical_psu)
        _2ndhorizlayout.addWidget(_connect_physical_PSU_button)

        _updateportsbutton = QPushButton("Update\nPorts")
        _updateportsbutton.clicked.connect(self.refreshports)
        _2ndhorizlayout.addWidget(_updateportsbutton)

        _connect_sensor_button = QPushButton("Connect\nsensor")
        _connect_sensor_button.clicked.connect(self.checkandconnect_sensor)
        _2ndhorizlayout.addWidget(_connect_sensor_button)
        _INITlayout.addLayout(_2ndhorizlayout)

        _separator_1 = QFrame()
        _separator_1.setFrameShape(QFrame.HLine)
        _separator_1.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        _separator_1.setLineWidth(5)

        _separator_2 = QFrame()
        _separator_2.setFrameShape(QFrame.HLine)
        _separator_2.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        _separator_2.setLineWidth(5)

        _INITlayout.addWidget(_separator_1)
        _INITlayout.addWidget(_separator_2)

# *************** PSUs used by Vgs PSU
        _3rddhorizlayout = QHBoxLayout()

        _VgsPSUlayout = QVBoxLayout()

        _VgsPSULabel = QLabel("In use by Vgs PSU")
        _VgsPSULabel.setMinimumSize(150, 50)
        _VgsPSUlayout.addWidget(_VgsPSULabel)

        self.VgsPSUsListWidget = QListWidget()
        self.VgsPSUsListWidget.setObjectName("Vgs PSU")
        self.VgsPSUsListWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.VgsPSUsListWidget.setMinimumSize(250, 35)
        self.VgsPSUsListWidget.adjustSize()
        self.VgsPSUsListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.VgsPSUsListWidget.setDefaultDropAction(Qt.MoveAction)
        self.VgsPSUsListWidget.model().rowsInserted.connect(lambda: self.background_color(self.VgsPSUsListWidget))
        self.VgsPSUsListWidget.model().rowsRemoved.connect(lambda: self.background_color(self.VgsPSUsListWidget))
        _VgsPSUlayout.addWidget(self.VgsPSUsListWidget)

        _VgsPSUlayout.addStretch()

        # *************** test PSU -- Polarity radio buttons

        _TestVgsButton = QPushButton('Test')
        _TestVgsButton.setMinimumSize(150, 65)
        _TestVgsButton.pressed.connect(lambda: self.test_psu("Vgs PSU"))
        _VgsPSUlayout.addWidget(_TestVgsButton)

        _VgsRadioButtonGrp = QButtonGroup()
        _polarityVgsPSUlayout = QVBoxLayout()
        vgs_polarity = QRadioButton("Source negative")
        _VgsPSUlayout.addWidget(vgs_polarity)
        vgs_polarity.setChecked(self.PSUdict["Vgs PSU"].polarity)
        vgs_polarity.toggled.connect(self.Vgspolaritychanged.emit)
        vgs_polarity2 = QRadioButton("Source positive")
        _VgsPSUlayout.addWidget(vgs_polarity2)
        vgs_polarity2.setChecked(not self.PSUdict["Vgs PSU"].polarity)

        _VgsRadioButtonGrp.addButton(vgs_polarity)
        _VgsRadioButtonGrp.addButton(vgs_polarity2)

        _VgsPSUlayout.addLayout(_polarityVgsPSUlayout)
        _3rddhorizlayout.addLayout(_VgsPSUlayout)

        _VgsPSUlayout.addStretch()

# *************** Available PSUs

        _initPSUlayout = QVBoxLayout()

        _AvailablePsusLabel = QLabel("Available PSUs")
        _AvailablePsusLabel.setMinimumSize(150, 50)
        _initPSUlayout.addWidget(_AvailablePsusLabel)

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

        _DisconnectPhysicalPsuButton = QPushButton('Disconnect')
        _DisconnectPhysicalPsuButton.setMinimumSize(150, 65)
        _DisconnectPhysicalPsuButton.pressed.connect(self.disconnect_physical_psu)
        _initPSUlayout.addWidget(_DisconnectPhysicalPsuButton)

        _ExitButton = QPushButton('Exit')
        _ExitButton.setMinimumSize(150, 65)
        _ExitButton.pressed.connect(self.hide)
        _initPSUlayout.addWidget(_ExitButton)

        _3rddhorizlayout.addLayout(_initPSUlayout)

# *************** PSUs used by Vds PSU

        _VdsPSUlayout = QVBoxLayout()

        _VdsPSUsListLabel = QLabel("In use by Vds PSU")
        _VdsPSUsListLabel.setMinimumSize(150, 50)
        _VdsPSUlayout.addWidget(_VdsPSUsListLabel)

        self.VdsPSUsListWidget = QListWidget()
        self.VdsPSUsListWidget.setObjectName("Vds PSU")
        self.VdsPSUsListWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.VdsPSUsListWidget.setMinimumSize(250, 35)
        self.VdsPSUsListWidget.adjustSize()
        self.VdsPSUsListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.VdsPSUsListWidget.setDefaultDropAction(Qt.MoveAction)
        self.VdsPSUsListWidget.model().rowsInserted.connect(lambda: self.background_color(self.VdsPSUsListWidget))
        self.VdsPSUsListWidget.model().rowsRemoved.connect(lambda: self.background_color(self.VdsPSUsListWidget))
        _VdsPSUlayout.addWidget(self.VdsPSUsListWidget)

        _VdsPSUlayout.addStretch()
        # ***************  test PSU --Polarity

        _TestVdsButton = QPushButton('Test')
        _TestVdsButton.setMinimumSize(150, 65)
        _TestVdsButton.pressed.connect(lambda: self.test_psu("Vds PSU"))
        _VdsPSUlayout.addWidget(_TestVdsButton)

        _VdsRadioButtonGrp = QButtonGroup()
        _polarityVdsPSUlayout = QVBoxLayout()
        vds_polarity = QRadioButton("Source negative")
        _polarityVdsPSUlayout.addWidget(vds_polarity)
        vds_polarity.setChecked(self.PSUdict["Vds PSU"].polarity)
        vds_polarity.toggled.connect(self.Vdspolaritychanged.emit)
        vds_polarity2 = QRadioButton("Source positive")
        _polarityVdsPSUlayout.addWidget(vds_polarity2)
        vds_polarity2.setChecked(not self.PSUdict["Vds PSU"].polarity)

        _VdsRadioButtonGrp.addButton(vds_polarity)
        _VdsRadioButtonGrp.addButton(vds_polarity2)

        _VdsPSUlayout.addLayout(_polarityVdsPSUlayout)

        _VdsPSUlayout.addStretch()

        _3rddhorizlayout.addLayout(_VdsPSUlayout)

        # *************** PSUs used by Heater

        _separator_3 = QFrame()
        _separator_3.setFrameShape(QFrame.VLine)
        _separator_3.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        _separator_3.setLineWidth(5)

        _3rddhorizlayout.addWidget(_separator_3)

        _HeaterPSUlayout = QVBoxLayout()

        _HeaterPSULabel = QLabel("In use by Heater")
        _HeaterPSULabel.setMinimumSize(150, 50)
        _HeaterPSUlayout.addWidget(_HeaterPSULabel)

        self.HeaterPSUsListWidget = QListWidget()
        self.HeaterPSUsListWidget.setObjectName("Heater PSU")
        self.HeaterPSUsListWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.HeaterPSUsListWidget.setMinimumSize(250, 35)
        self.HeaterPSUsListWidget.adjustSize()
        self.HeaterPSUsListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.HeaterPSUsListWidget.setDefaultDropAction(Qt.MoveAction)
        self.HeaterPSUsListWidget.model().rowsInserted.connect(lambda: self.background_color(self.HeaterPSUsListWidget))
        self.HeaterPSUsListWidget.model().rowsRemoved.connect(lambda: self.background_color(self.HeaterPSUsListWidget))
        _HeaterPSUlayout.addWidget(self.HeaterPSUsListWidget)

        _TestHeaterButton = QPushButton('Test')
        _TestHeaterButton.setMinimumSize(150, 65)
        _TestHeaterButton.pressed.connect(lambda: self.test_psu("Heater PSU"))
        _HeaterPSUlayout.addWidget(_TestHeaterButton)

        _3rddhorizlayout.addLayout(_HeaterPSUlayout)

        _VgsPSUlayout.addStretch()

        # *************** temperature sensor connected

        _sensorConnectedlayout = QVBoxLayout()

        _sensorConnectedLabel = QLabel("Temperature sensor")
        _sensorConnectedLabel.setMinimumSize(150, 50)
        _sensorConnectedlayout.addWidget(_sensorConnectedLabel)

        self.sensorConnectedPlaceholder = QLabel()
        self.sensorConnectedPlaceholder.setMinimumSize(150, 50)
        _sensorConnectedlayout.addWidget(self.sensorConnectedPlaceholder)

        _DisconnectSensorButton = QPushButton('Disconnect sensor')
        _DisconnectSensorButton.setMinimumSize(150, 65)
        _DisconnectSensorButton.pressed.connect(self.disconnect_sensor)
        _sensorConnectedlayout.addWidget(_DisconnectSensorButton)
        _sensorConnectedlayout.addStretch()

        _3rddhorizlayout.addLayout(_sensorConnectedlayout)

        _INITlayout.addLayout(_3rddhorizlayout)

    def background_color(self, widget):
        self.poller = QTimer(self)
        self.poller.setSingleShot(True)
        self.poller.timeout.connect(lambda: self.check_and_change(widget))
        self.poller.start(1)

    def check_and_change(self, widget):
        if (sorted([n.name for n in self.PSUdict[widget.objectName()].physical_psu_objects_list]) ==
                sorted([widget.item(n).text() for n in range(widget.count())])) or \
                ([n.name for n in self.PSUdict[widget.objectName()].physical_psu_objects_list][0] == "Empty PSU" and widget.count() == 0):
            widget.setStyleSheet("QWidget {background-color: lightgreen;}")
            self.InitButton.setStyleSheet("")
        else:
            widget.setStyleSheet("QWidget {background-color: red;}")
            self.InitButton.setStyleSheet("QWidget {background-color: red;}")

    def test_psu(self, psu):
        if not any([x in self.PSUdict[psu].name for x in ("Empty PSU", "Test PSU")]):
            self.PSUdict[psu].enableoutput(False)
            for i in range(2):
                for physicalpsu in self.PSUdict[psu].physical_psu_objects_list:
                    physicalpsu.setcurrent(float("1." + "9" * physicalpsu.VRESSETCNT))
                time.sleep(0.5)
                for physicalpsu in self.PSUdict[psu].physical_psu_objects_list:
                    physicalpsu.setcurrent(0)
                    time.sleep(0.5)

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
                    popup_message("Temperature probe CONECTED\n" + mystdout.getvalue())

            except BaseException as e:
                self.PSUdict["Temperature Sensor"] = None
                if verbose:
                    popup_message(str(e))
        else:
            popup_message("Sensor : " + self.sensorConnectedPlaceholder.text() + "\n is already connected")

    def disconnect_sensor(self):
        if len(self.sensorConnectedPlaceholder.text()) > 0:
            usedports.remove(self.sensorConnectedPlaceholder.text().strip().split("\n")[-1])
            self.PSUdict["Temperature Sensor"] = None
            self.sensorConnectedPlaceholder.setText("")
            self.refreshports()

    def serial_ports(self):
        _result = ([comport.device for comport in serial.tools.list_ports.comports()])
        _result.append("Test_Vgs_Port")
        _result.append("Test_Vds_Port")
        for p in usedports:
            if p in _result:
                _result.remove(p)
        return _result

    def refreshports(self):
        self.PortsListWidget.clear()
        self.PortsListWidget.addItems(self.serial_ports())

    def checkandconnect_physical_psu(self):
        if len(self.PSUsListWidget.selectedItems()) > 0 and len(self.PortsListWidget.selectedItems()) > 0:
            _ready_psu_name = self.connect_physical_psu(physicalpsusClasses[self.PSUsListWidget.currentItem().text()],
                                                        self.PortsListWidget.currentItem().text(), True)
            self.AvailablePSUsWidget.addItem(_ready_psu_name)
            self.PortsListWidget.takeItem(self.PortsListWidget.currentRow())
            self.refreshports()

    def connect_physical_psu(self, _psu_class, _selected_port, verbose=False):
        try:
            _physical_psu_instance = _psu_class(_selected_port)
            _ready_psu_name = str(_physical_psu_instance.name + " / " + _physical_psu_instance.MODEL +
                                 "\n   at port: " + _physical_psu_instance.port)
            _physical_psu_instance.name = _ready_psu_name
            AvailablePSUs.update({_ready_psu_name: _physical_psu_instance})
            usedports.append(_selected_port)
            self.refreshports()
            return _ready_psu_name

        except (IOError, RuntimeError) as e:
            if verbose:
                print(e)
                popup_message(str(e))
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

        for names, list_object in [(_VgsPSUsSelected, self.VgsPSUsListWidget),
                           (_VdsPSUsSelected, self.VdsPSUsListWidget),
                           (_HeaterPSUsSelected, self.HeaterPSUsListWidget)]:
            match len(names):
                case 0:
                    self.PSUdict[list_object.objectName()] = VirtualPSU([EmptyPSU()])
                case 1:
                    self.PSUdict[list_object.objectName()] = VirtualPSU([AvailablePSUs[names[0]]])
                case _ if len(names) > 1:
                    self.PSUdict[list_object.objectName()] = VirtualPSU([AvailablePSUs[name] for name in names])
                case _:
                    return
            self.background_color(list_object)

        self.updateMainWindow.emit()

    def applysettings(self):
        if len(self.settings.allKeys()) == 0:
            return

        try:
            _vgs_settings = self.settings.value("Vgs physical PSU objects")
            _vds_settings = self.settings.value("Vds physical PSU objects")
            _heater_settings = self.settings.value("Heater physical PSU objects")

            for psu, settings in (("Vgs PSU", _vgs_settings), ("Vds PSU", _vds_settings), ("Heater PSU", _heater_settings)):
                if settings is None or settings[0][0] == "Empty PSU":
                    pass
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
                                if psu == "Vgs PSU":
                                    self.settings.setValue("Vgs physical PSU objects", ["Empty PSU", 'None'])
                                elif psu == "Vds PSU":
                                    self.settings.setValue("Vds physical PSU objects", ["Empty PSU", 'None'])
                                elif psu == "Heater PSU":
                                    self.settings.setValue("Heater physical PSU objects", ["Empty PSU", 'None'])
                                self.settings.setValue(psu, "Empty PSU")
                            self.PSUdict[psu] = VirtualPSU([EmptyPSU()])
            self.create_virtual_psus()

            self.PSUdict["Vgs PSU"].VSTARTwidget.widgetSpinbox.setValue(float(self.settings.value("Vgs PSU start")))
            self.PSUdict["Vgs PSU"].VENDwidget.widgetSpinbox.setValue(float(self.settings.value("Vgs PSU end")))
            self.PSUdict["Vgs PSU"].STEPwidget.widgetSpinbox.setValue(float(self.settings.value("Vgs PSU step")))
            self.PSUdict["Vgs PSU"].IMAXwidget.widgetSpinbox.setValue(int(self.settings.value("Vgs PSU Imax")))

            self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.setValue(float(self.settings.value("Vds PSU start")))
            self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.setValue(float(self.settings.value("Vds PSU end")))
            self.PSUdict["Vds PSU"].STEPwidget.widgetSpinbox.setValue(float(self.settings.value("Vds PSU step")))
            self.PSUdict["Vds PSU"].IMAXwidget.widgetSpinbox.setValue(int(self.settings.value("Vds PSU Imax")))

            self.PSUdict["DUT settings"].DUTMaxPSpinbox.setValue(int(self.settings.value("Pmax")))
            self.PSUdict["DUT settings"].TempSpinbox.setValue(int(self.settings.value("Temp")))

            self.connect_sensor(self.settings.value("Temperature Sensor").strip().split("\n")[0],
                                self.settings.value("Temperature Sensor").strip().split("\n")[-1])

        except(KeyError, TypeError, ValueError) as e:
            self.PSUdict["Vgs PSU"] = VirtualPSU([EmptyPSU()])
            self.PSUdict["Vds PSU"] = VirtualPSU([EmptyPSU()])
            self.PSUdict["Heater PSU"] = VirtualPSU([EmptyPSU()])
            print("1111" + str(e))

        except BaseException as e:
            self.settings.clear()
            print("222222" + str(e))

    def savesettings(self):

        _vgs_psu_class_names_and_ports = []
        _vds_psu_class_names_and_ports = []
        _heater_psu_class_names_and_ports = []

        for psu_object in self.PSUdict["Vgs PSU"].physical_psu_objects_list:
            _vgs_psu_class_names_and_ports.append((getkey(psu_object.__class__), psu_object.port))

        for psu_object in self.PSUdict["Vds PSU"].physical_psu_objects_list:
            _vds_psu_class_names_and_ports.append((getkey(psu_object.__class__), psu_object.port))

        for psu_object in self.PSUdict["Heater PSU"].physical_psu_objects_list:
            _heater_psu_class_names_and_ports.append((getkey(psu_object.__class__), psu_object.port))

        self.settings.setValue("Vgs physical PSU objects", _vgs_psu_class_names_and_ports)
        self.settings.setValue("Vgs PSU start", self.PSUdict["Vgs PSU"].VSTARTwidget.widgetSpinbox.value())
        self.settings.setValue("Vgs PSU end", self.PSUdict["Vgs PSU"].VENDwidget.widgetSpinbox.value())
        self.settings.setValue("Vgs PSU step", self.PSUdict["Vgs PSU"].STEPwidget.widgetSpinbox.value())
        self.settings.setValue("Vgs PSU Imax", self.PSUdict["Vgs PSU"].IMAXwidget.widgetSpinbox.value())

        self.settings.setValue("Vds physical PSU objects", _vds_psu_class_names_and_ports)
        self.settings.setValue("Vds PSU start", self.PSUdict["Vds PSU"].VSTARTwidget.widgetSpinbox.value())
        self.settings.setValue("Vds PSU end", self.PSUdict["Vds PSU"].VENDwidget.widgetSpinbox.value())
        self.settings.setValue("Vds PSU step", self.PSUdict["Vds PSU"].STEPwidget.widgetSpinbox.value())
        self.settings.setValue("Vds PSU Imax", self.PSUdict["Vds PSU"].IMAXwidget.widgetSpinbox.value())

        self.settings.setValue("Heater physical PSU objects", _heater_psu_class_names_and_ports)

        self.settings.setValue("Pmax", self.PSUdict["DUT settings"].DUTMaxPSpinbox.value())
        self.settings.setValue("Temp", self.PSUdict["DUT settings"].TempSpinbox.value())

        self.settings.setValue("Temperature Sensor", (self.sensorConnectedPlaceholder.text()))



