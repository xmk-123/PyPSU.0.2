
import serial
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMainWindow, QListWidget, QRadioButton, \
    QMessageBox, QLabel, QToolButton, QButtonGroup
import logging
import serial.tools.list_ports

from serial import SerialException

import curvetracePSU
import powersupply_KORAD
from powersupply_COMPOSITE import PSUCOMPOSITE
from powersupply_EMPTY import EmptyPSU

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

physicalpsus = {"Korad": powersupply_KORAD.KORAD, "Test": None}
AvailablePSUs = {}


class PsuInitWindow(QMainWindow):

    Vgspolaritychanged = pyqtSignal(bool)
    Vdspolaritychanged = pyqtSignal(bool)
    updateMainWindow = pyqtSignal(bool)

    def __init__(self, PSUdict):
        super().__init__()
        self.PSUdict = PSUdict
        self.window = QWidget()
        self.setWindowTitle(" setup ")
        _layout = QVBoxLayout()
        self.setCentralWidget(self.window)
        self.window.setLayout(_layout)
# *************** PSUs list - Ports list

        _1sthorizlayout = QHBoxLayout()

        _psusLayout = QVBoxLayout()
        self.PsusLabel = QLabel("PSUs list")
        self.PsusLabel.setMinimumSize(150, 50)
        _psusLayout.addWidget(self.PsusLabel)

        self.PSUsListWidget = QListWidget()
        self.PSUsListWidget.addItems(physicalpsus.keys())
        self.PSUsListWidget.setMinimumSize(250, 35)
        self.PSUsListWidget.adjustSize()
        self.PSUsListWidget.currentItemChanged.connect(lambda p: self.initpsubutton.setText("Init\n %s PSU" % p.text()))
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

        _layout.addLayout(_1sthorizlayout)
# *************** init psu - Update ports  buttons

        _2ndhorizlayout = QHBoxLayout()

        self.initpsubutton = QPushButton("Init PSU")
        self.initpsubutton.clicked.connect(self.ConnectPSU)
        _2ndhorizlayout.addWidget(self.initpsubutton)

        self.updateportsbutton = QPushButton("Update\nPorts")
        self.updateportsbutton.clicked.connect(self.refreshports)
        _2ndhorizlayout.addWidget(self.updateportsbutton)
        _layout.addLayout(_2ndhorizlayout)

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
        self.VgsPSUsListWidget.addItems(AvailablePSUs.keys())
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
        self.addToVgsPSUbutton.clicked.connect(lambda x: self.addToPSU(self.VgsPSUsListWidget))
        addremoveVgsPSUbuttonlayout.addWidget(self.addToVgsPSUbutton)

        self.removefromVgsPSUbutton = QToolButton()
        self.removefromVgsPSUbutton.setArrowType(QtCore.Qt.RightArrow)
        self.removefromVgsPSUbutton.clicked.connect(lambda x: self.removefromPSU(self.VgsPSUsListWidget))
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
        self.AvailablePSUsWidget.addItems(AvailablePSUs.keys())
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

        # *************** Initialize button - exit button

        self.InitButton = QPushButton('Create')
        self.InitButton.setMinimumSize(150, 65)
        self.InitButton.pressed.connect(self.InitPSU)
        _initPSUlayout.addWidget(self.InitButton)

        self.ExitButton = QPushButton('Exit')
        self.ExitButton.setMinimumSize(150, 65)
        self.ExitButton.pressed.connect(self.closewin)
        _initPSUlayout.addWidget(self.ExitButton)

        _3rddhorizlayout.addLayout(_initPSUlayout)

        # *************** add/remove ready PSU button

        addremoveVdsPSUbuttonlayout = QVBoxLayout()

        addremoveVdsPSUbuttonlayout.addStretch()
        self.removefromVdsPSUbutton = QToolButton()
        self.removefromVdsPSUbutton.setArrowType(QtCore.Qt.RightArrow)
        self.removefromVdsPSUbutton.clicked.connect(lambda x: self.addToPSU(self.VdsPSUsListWidget))
        addremoveVdsPSUbuttonlayout.addWidget(self.removefromVdsPSUbutton)

        self.addToVdsPSUbutton = QToolButton()
        self.addToVdsPSUbutton.setArrowType(QtCore.Qt.LeftArrow)
        self.addToVdsPSUbutton.clicked.connect(lambda x: self.removefromPSU(self.VdsPSUsListWidget))
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
        self.VdsPSUsListWidget.addItems(AvailablePSUs.keys())
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

        _layout.addLayout(_3rddhorizlayout)

    def addToPSU(self, psulistwidget):
        for i in self.AvailablePSUsWidget.selectedItems():
            psulistwidget.addItem(i.text())
            self.AvailablePSUsWidget.takeItem(self.AvailablePSUsWidget.row(i))

    def removefromPSU(self, psulistwidget):
        for i in psulistwidget.selectedItems():
            self.AvailablePSUsWidget.addItem(i.text())
            psulistwidget.takeItem(psulistwidget.row(i))

    def closewin(self):
        self.close()

    def serial_ports(self):
        result = ([comport.device for comport in serial.tools.list_ports.comports()])
        # result.insert(0, "None")
        return result

    def refreshports(self):
        self.PortsListWidget.clear()
        self.PortsListWidget.addItems(self.serial_ports())

    def ConnectPSU(self):

        if len(self.PSUsListWidget.selectedItems()) > 0 or len(self.PortsListWidget.selectedItems()) > 0:
            _PSUclass = physicalpsus[self.PSUsListWidget.selectedItems()[0].text()]
            _selectedPort = self.PortsListWidget.selectedItems()[0].text()
            try:
                curvtracePSU = curvetracePSU.createPSUclass(_PSUclass)(_selectedPort)
                readyPSUname = str(curvtracePSU.name + " / " + curvtracePSU.MODEL + "   at port:   " + curvtracePSU.port)
                AvailablePSUs.update({readyPSUname: curvtracePSU})
                self.AvailablePSUsWidget.addItem(readyPSUname)
                print(AvailablePSUs)

            except SerialException as e:
                logger.warning("error\n %s" % e)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(str(e))
                msg.setStandardButtons(QMessageBox.Close)
                msg.exec()
        else:
            return
            # QMessageBox.about(self, "Error", str(e))

    def DisconnectPSU(self):
        self.PSUdict[self.psuKey] = curvetracePSU.createPSUclass(EmptyPSU)
        for i in self.AvailablePSUsWidget.selectedItems():
            del AvailablePSUs[i.text()]
            self.AvailablePSUsWidget.takeItem(self.AvailablePSUsWidget.row(i))
        # del self.AvailablePSUs[self.AvailablePSUsWidget.selectedItems()]
        # self.AvailablePSUsWidget.takeItem(self.AvailablePSUsWidget.currentRow())

    def InitPSU(self):
        _VgsPSUs = [str(self.VgsPSUsListWidget.item(i).text()) for i in range(self.VgsPSUsListWidget.count())]
        _VdsPSUs = [str(self.VdsPSUsListWidget.item(i).text()) for i in range(self.VdsPSUsListWidget.count())]

        for p, key in [(_VgsPSUs, "Vgs PSU"), (_VdsPSUs, "Vds PSU")]:
            match len(p):
                case 0:
                    self.PSUdict[key] = curvetracePSU.createPSUclass(EmptyPSU)()
                    self.updatePSUwidgetssettings(key)
                case 1:
                    self.PSUdict[key] = AvailablePSUs[p[0]]
                    self.updatePSUwidgetssettings(key)
                case range(1, 10):
                    self.PSUdict[key] = PSUCOMPOSITE(p)
                    self.updatePSUwidgetssettings(key)
                case _:
                    return
        
        self.updateMainWindow.emit(True)

        #     self.close()

        # ports = [s for s in _selected]
        # if len(_PhysicalPSU) > 0:
        #     if len(ports) > 0:  # to select multiple entries
        #         if ports[0].text() == "None" and self.port is not None:
        #             self.serial = serial.Serial(self.port)
        #             self.serial.close()
        #             self.port = None

    def updatePSUwidgetssettings(self, key):
        return
        # self.psulabel.setText(self.self.PSUdict[key].MODEL)
        self.PSUdict[key].VSTARTwidget.widgetSpinbox.setDecimals(self.PSUdict[key].VRESSETCNT)
        self.PSUdict[key].VSTARTwidget.widgetSpinbox.setSingleStep(self.PSUdict[key].VRESSET)
        self.PSUdict[key].VSTARTwidget.widgetSpinbox.setMinimum(self.PSUdict[key].VMIN)
        self.PSUdict[key].VSTARTwidget.widgetSpinbox.setMaximum(self.PSUdict[key].VMAX)
        self.PSUdict[key].VENDwidget.widgetSpinbox.setDecimals(self.PSUdict[key].VRESSETCNT)
        self.PSUdict[key].VENDwidget.widgetSpinbox.setSingleStep(self.PSUdict[key].VRESSET)
        self.PSUdict[key].VENDwidget.widgetSpinbox.setMinimum(self.PSUdict[key].VMIN)
        self.PSUdict[key].VENDwidget.widgetSpinbox.setMaximum(self.PSUdict[key].VMAX)
        self.PSUdict[key].STEPwidget.widgetSpinbox.setDecimals(self.PSUdict[key].VRESSETCNT)
        self.PSUdict[key].STEPwidget.widgetSpinbox.setSingleStep(self.PSUdict[key].VRESSET)
        self.PSUdict[key].IMAXwidget.widgetSpinbox.setDecimals(self.PSUdict[key].IRESSETCNT)
        self.PSUdict[key].IMAXwidget.widgetSpinbox.setSingleStep(self.PSUdict[key].IRESSET)
        self.PSUdict[key].IMAXwidget.widgetSpinbox.setMaximum(self.PSUdict[key].IMAX)
        self.PSUdict[key].enablespinbxs(True)
