from PyQt5.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QWidget, QVBoxLayout

import powersupply_EMPTY
from powersupply_EMPTY import EmptyPSU


def createPSUclass(cls):
    class CurvetracePSU(cls, QWidget):
        def __init__(self, port=None):
            super().__init__(port)

            self.window = QWidget()
            self._layout = QVBoxLayout()
            self.window.setLayout(self._layout)

            self.polarity = True
            self.port = port
            self.VSTARTwidget = ParameterWidget("Start V", self.VMIN, self.VMAX, self.VRESSETCNT)
            self.VENDwidget = ParameterWidget("End V", self.VMIN, self.VMAX, self.VRESSETCNT)
            self.STEPwidget = ParameterWidget("Step V", self.VRESSET, self.VMAX, self.VRESSETCNT)
            self.IMAXwidget = ParameterWidget("Max I", 0, self.IMAX, self.IRESSETCNT)


            self._layout.addWidget(self.VSTARTwidget)
            self._layout.addWidget(self.VENDwidget)
            self._layout.addWidget(self.STEPwidget)
            self._layout.addWidget(self.IMAXwidget)

            
            if cls == EmptyPSU:
                self.enablespinbxs(False)
            else:
                self.enablespinbxs(True)

        def enablespinbxs(self, enable):
            for widget in self._layout.parentWidget().findChildren(QDoubleSpinBox):
                widget.setEnabled(enable)

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
