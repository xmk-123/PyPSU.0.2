from PyQt5.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QWidget, QVBoxLayout, QPushButton
import setup
from powersupply_EMPTY import EmptyPSU


def createPSUclass(cls):
    class CurvetracePSU(cls, QWidget):
        def __init__(self):
            super().__init__()


            self.window = QWidget()
            _layout = QVBoxLayout()
            self.window.setLayout(_layout)

            self.polarity = True

            self.VSTART = ParameterWidget("Start V", self.VMIN, self.VMAX, self.VRESSETCNT)
            self.VEND = ParameterWidget("End V", self.VMIN, self.VMAX, self.VRESSETCNT)
            self.IMAX = ParameterWidget("Max I", 0, self.IMAX, self.IRESSETCNT)
            self.STEP = ParameterWidget("Step V", (1/self.VRESSETCNT), self.VMAX, self.VRESSETCNT)
            _layout.addWidget(self.VSTART)
            _layout.addWidget(self.VEND)
            _layout.addWidget(self.IMAX)
            _layout.addWidget(self.STEP)


    class ParameterWidget(QWidget):
        def __init__(self, name, minval, maxval, resolution):
            super().__init__()
            _layout = QHBoxLayout()

            _widgetLabel = QLabel(name)
            _widgetLabel.setMinimumSize(110, 50)
            _layout.addWidget(_widgetLabel)

            self.widgetSpinbox = QDoubleSpinBox()
            self.widgetSpinbox.setMinimumSize(130, 50)
            self.widgetSpinbox.setMaximumSize(130, 50)
            self.widgetSpinbox.setMinimum(minval)
            self.widgetSpinbox.setMaximum(maxval)
            self.widgetSpinbox.setSingleStep(1/resolution)
            self.widgetSpinbox.setDecimals(resolution)
            _layout.addWidget(self.widgetSpinbox)

            self.setLayout(_layout)


    class PsuButtonBox(QWidget):
        def __init__(self):
            super().__init__()
            self.PsuSetupWin = None

            self.layout = QVBoxLayout()
            self.button = QPushButton("+                  +\n  " + self.parametersdictionary["name"]
                                      + "  \n-                 -")
            stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 red, stop: 0.51 dimgrey)}"
            self.button.setStyleSheet(stylesheet)
            self.button.setMinimumSize(150, 65)
            self.layout.addWidget(self.button)
            self.button.clicked.connect(self.openpsuwindow)

            self.setLayout(self.layout)

        def openpsuwindow(self):
            if self.PsuSetupWin is None:
                self.PsuSetupWin = psuinitialize.psuinitwindow.PsuWindow()
            self.PsuSetupWin.show()

        def set(self, value):
            if value:
                stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 red, stop: 0.51 dimgrey)}"
                self.button.setStyleSheet(stylesheet)
                self.button.setText('+                  +\n  PSU Vgs  \n-                 -')
            else:
                stylesheet = "QWidget {background-color: QLinearGradient(y1:0, y2:1, stop: 0.49 dimgrey, stop: 0.51 red)}"
                self.button.setStyleSheet(stylesheet)
                self.button.setText('-                  -\n  PSU Vgs  \n+                 +')

    return CurvetracePSU