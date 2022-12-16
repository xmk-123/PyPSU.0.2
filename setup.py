from gc import get_referrers

import serial
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMainWindow, QListWidget, QRadioButton, \
    QMessageBox, QLabel
import logging
import serial.tools.list_ports

from serial import SerialException

import curvetracePSU
import powersupply_KORAD
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

    polaritychanged = pyqtSignal(bool)
    updateMainWindow = pyqtSignal(bool)
    def __init__(self, PSUdict, psuKey):
        super().__init__()

        self.PSUdict = PSUdict
        self.psuKey = psuKey

        self.window = QWidget()
        self.setWindowTitle("%s setup " % psuKey)
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
# *************** Available PSUs

        self.AvailablePsusLabel = QLabel("Available PSUs")
        self.AvailablePsusLabel.setMinimumSize(150, 50)
        _layout.addWidget(self.AvailablePsusLabel)

        self.AvailablePSUsWidget = QListWidget()
        self.AvailablePSUsWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.AvailablePSUsWidget.setMinimumSize(250, 35)
        self.AvailablePSUsWidget.adjustSize()
        self.AvailablePSUsWidget.addItems(AvailablePSUs.keys())
        _layout.addWidget(self.AvailablePSUsWidget)

        # items = [self.PSUsListWidget.item(x).text() for x in range(self.PSUsListWidget.count())]
        # self.CurrentRow = items.index(str(self.psu.name))
        # self.PSUsListWidget.setCurrentRow(self.CurrentRow)
        # items = [self.PortsListWidget.item(x).text() for x in range(self.PortsListWidget.count())]
        # self.CurrentRow = items.index(str(self.port))
        # self.PortsListWidget.setCurrentRow(self.CurrentRow)

        # items = [self.AvailablePSUsWidget.item(x).text() for x in range(self.PortsListWidget.count())]
        # self.CurrentRow = items.index(str(self.psu.name))
        # self.PortsListWidget.setCurrentRow(self.CurrentRow)

        _layout.addStretch()
# *************** remove ready PSU button

        self.removepsubutton = QPushButton("Remove selected ready PSUs")
        self.removepsubutton.clicked.connect(self.DisconnectPSU)
        _layout.addWidget(self.removepsubutton)

# *************** Polarity

        RadioPolarity = QRadioButton("Source negative")
        _layout.addWidget(RadioPolarity)
        RadioPolarity.setChecked(self.PSUdict[psuKey].polarity)
        RadioPolarity.toggled.connect(lambda s: self.polaritychanged.emit(s))
        RadioPolarity2 = QRadioButton("Source positive")
        _layout.addWidget(RadioPolarity2)
        RadioPolarity2.setChecked(not self.PSUdict[psuKey].polarity)

        _layout.addStretch()
# *************** Initialize button
        _3rdhorizlayout = QHBoxLayout()

        self.InitButton = QPushButton('Create %s' % psuKey)
        self.InitButton.setMinimumSize(150, 65)
        self.InitButton.pressed.connect(self.InitPSU)
        _3rdhorizlayout.addWidget(self.InitButton)

        self.ExitButton = QPushButton('Exit')
        self.ExitButton.setMinimumSize(150, 65)
        self.ExitButton.pressed.connect(self.closewin)
        _3rdhorizlayout.addWidget(self.ExitButton)

        _layout.addLayout(_3rdhorizlayout)

        self.window.setWindowModality(QtCore.Qt.WindowModal)

    def closewin(self):
        self.close()

    def serial_ports(self):
        result = ([comport.device for comport in serial.tools.list_ports.comports()])
        #result.insert(0, "None")
        return result

    def refreshports(self):
        self.PortsListWidget.clear()
        self.PortsListWidget.addItems(self.serial_ports())

    def ConnectPSU(self):

        if len(self.PSUsListWidget.selectedItems()) > 0 and len(self.PSUsListWidget.selectedItems()) > 0:
            _PSUclass = physicalpsus[self.PSUsListWidget.selectedItems()[0].text()]
            _selectedPort = self.PortsListWidget.selectedItems()[0].text()
            try:
                curvtracePSU = curvetracePSU.createPSUclass(_PSUclass)(_selectedPort)
                readyPSUname = str(curvtracePSU.name + " / " + curvtracePSU.MODEL + "   at port:   " + curvtracePSU.port)
                AvailablePSUs.update({readyPSUname: curvtracePSU})
                self.AvailablePSUsWidget.addItem(readyPSUname)

          

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
        #self.AvailablePSUsWidget.takeItem(self.AvailablePSUsWidget.currentRow())


    def InitPSU(self):
        if len(self.AvailablePSUsWidget.selectedItems()) == 1:
            _ReadyPSUsSelected = self.AvailablePSUsWidget.selectedItems()[0].text()
            self.PSUdict[self.psuKey] = AvailablePSUs[_ReadyPSUsSelected]
            self.updatePSUwidgetssettings()
            self.updateMainWindow.emit(True)
            self.close()
        return
        ports = [s for s in _selected]
        if len(_PhysicalPSU) > 0:
            if len(ports) > 0:  # to select multiple entries
                if ports[0].text() == "None" and self.port is not None:
                    self.serial = serial.Serial(self.port)
                    self.serial.close()
                    self.port = None

    def updatePSUwidgetssettings(self):
        #self.psulabel.setText(self.self.PSUdict[self.psuKey].MODEL)
        self.PSUdict[self.psuKey].VSTARTwidget.widgetSpinbox.setDecimals(self.PSUdict[self.psuKey].VRESSETCNT)
        self.PSUdict[self.psuKey].VSTARTwidget.widgetSpinbox.setSingleStep(self.PSUdict[self.psuKey].VRESSET)
        self.PSUdict[self.psuKey].VSTARTwidget.widgetSpinbox.setMinimum(self.PSUdict[self.psuKey].VMIN)
        self.PSUdict[self.psuKey].VSTARTwidget.widgetSpinbox.setMaximum(self.PSUdict[self.psuKey].VMAX)
        self.PSUdict[self.psuKey].VENDwidget.widgetSpinbox.setDecimals(self.PSUdict[self.psuKey].VRESSETCNT)
        self.PSUdict[self.psuKey].VENDwidget.widgetSpinbox.setSingleStep(self.PSUdict[self.psuKey].VRESSET)
        self.PSUdict[self.psuKey].VENDwidget.widgetSpinbox.setMinimum(self.PSUdict[self.psuKey].VMIN)
        self.PSUdict[self.psuKey].VENDwidget.widgetSpinbox.setMaximum(self.PSUdict[self.psuKey].VMAX)
        self.PSUdict[self.psuKey].STEPwidget.widgetSpinbox.setDecimals(self.PSUdict[self.psuKey].VRESSETCNT)
        self.PSUdict[self.psuKey].STEPwidget.widgetSpinbox.setSingleStep(self.PSUdict[self.psuKey].VRESSET)
        self.PSUdict[self.psuKey].IMAXwidget.widgetSpinbox.setDecimals(self.PSUdict[self.psuKey].IRESSETCNT)
        self.PSUdict[self.psuKey].IMAXwidget.widgetSpinbox.setSingleStep(self.PSUdict[self.psuKey].IRESSET)
        self.PSUdict[self.psuKey].IMAXwidget.widgetSpinbox.setMaximum(self.PSUdict[self.psuKey].IMAX)
        self.PSUdict[self.psuKey].enablespinbxs(True)





