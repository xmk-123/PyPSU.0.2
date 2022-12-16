import serial
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

#physicalpsus = {"Empty psu": EmptyPSU, "Korad": powersupply_KORAD.KORAD}
physicalpsus = {"Korad": powersupply_KORAD.KORAD}
readyPSUs = {}
virtualpsus = {}

class PsuInitWindow(QMainWindow):

    polaritychanged = pyqtSignal(bool)
    setupPSUchange = pyqtSignal(object)

    def __init__(self, psu, buttontxt):
        super().__init__()
        self.psu = psu
        self.psuname = psu.name
        self.port = psu.port
        self.readyPSUs = {}

        self.window = QWidget()
        self.setWindowTitle("%s setup " % buttontxt)
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
# *************** Ready PSUs

        self.ReadyPsusLabel = QLabel("Ready PSUs")
        self.ReadyPsusLabel.setMinimumSize(150, 50)
        _layout.addWidget(self.ReadyPsusLabel)

        self.ReadyPSUsWidget = QListWidget()
        self.ReadyPSUsWidget.setSelectionMode(QListWidget.MultiSelection)  # to select multiple entries
        self.ReadyPSUsWidget.setMinimumSize(250, 35)
        self.ReadyPSUsWidget.adjustSize()
        _layout.addWidget(self.ReadyPSUsWidget)

        # items = [self.PSUsListWidget.item(x).text() for x in range(self.PSUsListWidget.count())]
        # self.CurrentRow = items.index(str(self.psu.name))
        # self.PSUsListWidget.setCurrentRow(self.CurrentRow)
        # items = [self.PortsListWidget.item(x).text() for x in range(self.PortsListWidget.count())]
        # self.CurrentRow = items.index(str(self.port))
        # self.PortsListWidget.setCurrentRow(self.CurrentRow)

        # items = [self.ReadyPSUsWidget.item(x).text() for x in range(self.PortsListWidget.count())]
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
        RadioPolarity.setChecked(self.psu.polarity)
        RadioPolarity.toggled.connect(lambda s: self.polaritychanged.emit(s))
        RadioPolarity2 = QRadioButton("Source positive")
        _layout.addWidget(RadioPolarity2)
        RadioPolarity2.setChecked(not self.psu.polarity)

        _layout.addStretch()
# *************** Initialize button

        self.InitButton = QPushButton('Create %s' % buttontxt)
        self.InitButton.setMinimumSize(150, 65)
        self.InitButton.pressed.connect(self.InitPSU)
        _layout.addWidget(self.InitButton)

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
                self.readyPSUs.update({readyPSUname: curvtracePSU})
                self.ReadyPSUsWidget.addItem(readyPSUname)
                #virtualpsus[str(curvtracePSU.name + " / " + curvtracePSU.MODEL + "   at port:   " + curvtracePSU.port)] = curvtracePSU
                #curvtracePSU.name = curvtracePSU.name + " / " + curvtracePSU.MODEL + "   at port:   " + curvtracePSU.port

                #self.updatemainwindowwidgetssettings()
               # logger.info("PSU _selected : %s" % self.psu.MODEL)
                #self.close()

            except SerialException as e:
                logger.warning("error\n %s" % e)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(str(e))
                msg.setStandardButtons(QMessageBox.Close)
                msg.exec()
        else:
            return

        if _PSUclass is EmptyPSU:
            return


                # QMessageBox.about(self, "Error", str(e))
            # if len(_selectedPort) > 0:
            #     if _selectedPort[0].text() == "None" and self.port is not None:
            #         self.serial = serial.Serial(self.port)
            #         self.serial.close()
            #         self.port = None
    def DisconnectPSU(self):
        if self.readyPSUscount >= 1:
            del self.readyPSUs[self.ReadyPSUsWidget.currentRow()]
            self.ReadyPSUsWidget.takeItem(self.ReadyPSUsWidget.currentRow())

    def InitPSU(self):
        if len(self.ReadyPSUsWidget.selectedItems()) == 1:
            _ReadyPSUsSelected = self.ReadyPSUsWidget.selectedItems()
            self.setupPSUchange.emit(_ReadyPSUsSelected)

        return
        ports = [s for s in _selected]
        if len(_PhysicalPSU) > 0:
            if len(ports) > 0:  # to select multiple entries
                if ports[0].text() == "None" and self.port is not None:
                    self.serial = serial.Serial(self.port)
                    self.serial.close()
                    self.parametersdictionary["psuobject"] = None
                    self.port = None

    def updatemainwindowwidgetssettings(self):
        self.psulabel.setText(self.psu.MODEL)
        self.parametersdictionary["Start V"]["widget"].widgetSpinbox.setDecimals(self.psu.VRESSETCNT)
        self.parametersdictionary["Start V"]["widget"].widgetSpinbox.setSingleStep(self.psu.VRESSET)
        self.parametersdictionary["Start V"]["widget"].widgetSpinbox.setMinimum(self.psu.VMIN)
        self.parametersdictionary["Start V"]["widget"].widgetSpinbox.setMaximum(self.psu.VMAX)
        self.parametersdictionary["End V"]["widget"].widgetSpinbox.setDecimals(self.psu.VRESSETCNT)
        self.parametersdictionary["End V"]["widget"].widgetSpinbox.setSingleStep(self.psu.VRESSET)
        self.parametersdictionary["End V"]["widget"].widgetSpinbox.setMinimum(self.psu.VMIN)
        self.parametersdictionary["End V"]["widget"].widgetSpinbox.setMaximum(self.psu.VMAX)
        self.parametersdictionary["Step V"]["widget"].widgetSpinbox.setDecimals(self.psu.VRESSETCNT)
        self.parametersdictionary["Step V"]["widget"].widgetSpinbox.setSingleStep(self.psu.VRESSET)
        self.parametersdictionary["Max I"]["widget"].widgetSpinbox.setDecimals(self.psu.IRESSETCNT)
        self.parametersdictionary["Max I"]["widget"].widgetSpinbox.setSingleStep(self.psu.IRESSET)
        self.parametersdictionary["Max I"]["widget"].widgetSpinbox.setMaximum(self.psu.IMAX)





