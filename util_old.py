import sys
import glob
import serial
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QPushButton, QMessageBox, QListWidget, QHBoxLayout, \
    QMainWindow
import logging
from serial import SerialException
import serial.tools.list_ports

import powersupply_KORAD

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class PsuInitWindow(QMainWindow):
    def __init__(self, parametersdictionary):
        super().__init__()
        self.parametersdictionary = parametersdictionary
        self.psuname = self.parametersdictionary["name"]
        self.psulabel = self.parametersdictionary["label"]
        self.psu = parametersdictionary["psuobject"]

        if self.psu is not None:
            print(self.psu)
            self.port = self.parametersdictionary["psuobject"].port
        else:
            self.port = None

        self.window = QWidget()
        self.setWindowTitle("%s setup " % self.psuname)
        self.layout = QVBoxLayout()
        self.layout1 = QHBoxLayout()
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)

        self.PortsListWidget = QListWidget()
        # self.PortsListWidget.setSelectionMode(2)   to select multiple entries
        self.PortsListWidget.addItems(serial_ports())
        self.PortsListWidget.setMinimumSize(250, 35)
        self.PortsListWidget.adjustSize()
        self.layout1.addWidget(self.PortsListWidget)

        if self.port is not None:
            print(self.port)
            items = [self.PortsListWidget.item(x).text() for x in range(self.PortsListWidget.count())]
            self.CurrentRow = items.index(self.port)
            self.PortsListWidget.setCurrentRow(self.CurrentRow)

        self.updateportsbutton = QPushButton("Update\nPorts")
        self.updateportsbutton.clicked.connect(self.refreshports)
        self.layout1.addWidget(self.updateportsbutton)

        self.layout.addLayout(self.layout1)
        self.layout.addStretch()

    # Polarity
        RadioPolarity = QRadioButton("Source negative")
        self.layout.addWidget(RadioPolarity)
        RadioPolarity.setChecked(True)
        self.parametersdictionary["Polarity"] = RadioPolarity
        RadioPolarity.setChecked(self.parametersdictionary["Polarity"].isChecked())
        RadioPolarity.toggled.connect(self.SetPolarity)
        RadioPolarity2 = QRadioButton("Source positive")
        self.layout.addWidget(RadioPolarity2)

        self.layout.addStretch()
    # Initialise button
        self.InitButton = QPushButton('Initialise %s' % self.psuname)
        self.InitButton.setMinimumSize(150, 65)
        self.InitButton.pressed.connect(self.InitPSU)
        self.layout.addWidget(self.InitButton)

    def InitPSU(self):

        selected = self.PortsListWidget.selectedItems()
        ports = [s for s in selected]
        if len(ports) > 0:                                    # to select multiple entries
            if ports[0].text() == "None" and self.port is not None:
                self.serial = serial.Serial(self.port)
                self.serial.close()
                self.parametersdictionary["psuobject"] = None
                self.port = None
            else:
                try:
                    self.psu = powersupply_KORAD.KORAD(ports[0].text(), True)
                    self.parametersdictionary["psuobject"] = self.psu
                    self.parametersdictionary["portwidgetitem"] = ports[0]

                    self.updatemainwindowwidgetssettings()
                    logger.info("PSU selected : %s" % self.psu.MODEL)
                    self.close()

                except SerialException as e:
                    logger.warning("error\n %s" % e)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText(str(e))
                    msg.setStandardButtons(QMessageBox.Close)
                    msg.exec()
                    # QMessageBox.about(self, "Error", str(e))
            self.close()

    def SetPolarity(self, polarity):
        if polarity:
            self.parametersdictionary["PSU button"].set(True)
        else:
            self.parametersdictionary["PSU button"].set(False)

    def refreshports(self):
        self.PortsListWidget.clear()
        self.PortsListWidget.addItems(serial_ports())

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


def serial_ports():
    result = ([comport.device for comport in serial.tools.list_ports.comports()])
    result.insert(0, "None")
    return result
