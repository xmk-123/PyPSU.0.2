from PyQt5.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QWidget, QVBoxLayout

import powersupply_EMPTY
from powersupply_EMPTY import EmptyPSU


def createPSUclass(cls):
    class CurvetracePSU(cls, QWidget):
        def __init__(self, port=None):
            super().__init__(port)

            self.window = QWidget()
            _layout = QVBoxLayout()
            self.window.setLayout(_layout)

            self.polarity = True
            self.port = port
            self.VSTART = ParameterWidget("Start V", self.VMIN, self.VMAX, self.VRESSETCNT)
            self.VEND = ParameterWidget("End V", self.VMIN, self.VMAX, self.VRESSETCNT)
            self.IMAX = ParameterWidget("Max I", 0, self.IMAX, self.IRESSETCNT)
            self.STEP = ParameterWidget("Step V", (1/self.VRESSETCNT), self.VMAX, self.VRESSETCNT)

            _layout.addWidget(self.VSTART)
            _layout.addWidget(self.VEND)
            _layout.addWidget(self.IMAX)
            _layout.addWidget(self.STEP)

        # def disablespinbxs(self, ):
            if cls == EmptyPSU:
                for widget in _layout.parentWidget().findChildren(QDoubleSpinBox):
                    widget.setDisabled(True)

    class ParameterWidget(QWidget):
        def __init__(self, name, minval, maxval, resolution):
            super().__init__()
            _layout2 = QHBoxLayout()

            _widgetLabel = QLabel(name)
            _widgetLabel.setMinimumSize(110, 50)
            _layout2.addWidget(_widgetLabel)

            self.widgetSpinbox = QDoubleSpinBox()
            self.widgetSpinbox.setMinimumSize(130, 50)
            self.widgetSpinbox.setMaximumSize(130, 50)
            self.widgetSpinbox.setMinimum(minval)
            self.widgetSpinbox.setMaximum(maxval)
            self.widgetSpinbox.setSingleStep(1/resolution)
            self.widgetSpinbox.setDecimals(resolution)
            _layout2.addWidget(self.widgetSpinbox)

            self.setLayout(_layout2)

    return CurvetracePSU
