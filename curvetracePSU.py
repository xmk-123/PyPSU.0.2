from PyQt5.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QWidget, QVBoxLayout
from powersupply_EMPTY import EmptyPSU


def createPSUclass(cls):
    class CurvetracePSU(cls, QWidget):
        def __init__(self, port=None):
            super().__init__(port)

            if self.VRESSET > 0:

                self.PSUwindow = QWidget()
                self._PSUlayout = QVBoxLayout()
                self.PSUwindow.setLayout(self._PSUlayout)

                self.polarity = True
                self.port = port
                self.VSTARTwidget = ParameterWidget("Start V", max(self.VMIN, self.VRESSET), self.VMAX, self.VRESSET, self.VRESSETCNT)
                self.VENDwidget = ParameterWidget("End V", max(self.VMIN, self.VRESSET), self.VMAX, self.VRESSET, self.VRESSETCNT)
                self.STEPwidget = ParameterWidget("Step V", self.VRESSET, self.VMAX, self.VRESSET, self.VRESSETCNT)
                self.IMAXwidget = ParameterWidget("Max I", 0, self.IMAX, self.IRESSET, self.IRESSETCNT)

                self._PSUlayout.addWidget(self.VSTARTwidget)
                self._PSUlayout.addWidget(self.VENDwidget)
                self._PSUlayout.addWidget(self.STEPwidget)
                self._PSUlayout.addWidget(self.IMAXwidget)

                self.VSTARTwidget.widgetSpinbox.valueChanged.connect(self.Vstartconditions)
                self.VENDwidget.widgetSpinbox.valueChanged.connect(self.Vendconditions)

                self.enablespinbxs(cls != EmptyPSU)

        def Vstartconditions(self, value):
            if value > self.VENDwidget.widgetSpinbox.value():
                self.VENDwidget.widgetSpinbox.setValue(self.VSTARTwidget.widgetSpinbox.value())

        def Vendconditions(self, value):
            if value < self.VSTARTwidget.widgetSpinbox.value():
                self.VSTARTwidget.widgetSpinbox.setValue(self.VENDwidget.widgetSpinbox.value())

        def enablespinbxs(self, enable):
            for widget in self._PSUlayout.parentWidget().findChildren(QDoubleSpinBox):
                widget.setEnabled(enable)

    class ParameterWidget(QWidget):
        def __init__(self, name, minval, maxval, minstep, resolution):
            super().__init__()
            self._PSUlayout2 = QHBoxLayout()

            self._widgetLabel = QLabel(name)
            self._widgetLabel.setMinimumSize(110, 50)
            self._PSUlayout2.addWidget(self._widgetLabel)

            self.widgetSpinbox = QDoubleSpinBox()
            self.widgetSpinbox.setMinimumSize(130, 50)
            self.widgetSpinbox.setMaximumSize(130, 50)
            self.widgetSpinbox.setMinimum(minval)
            self.widgetSpinbox.setMaximum(maxval)
            self.widgetSpinbox.setSingleStep(minstep)
            self.widgetSpinbox.setDecimals(resolution)
            self._PSUlayout2.addWidget(self.widgetSpinbox)

            self.setLayout(self._PSUlayout2)

    return CurvetracePSU
