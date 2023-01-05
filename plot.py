import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from scipy.interpolate import make_interp_spline
import copy


class PlotWin(QWidget):
    def __init__(self):
        super().__init__()

        self.plotline = []
        self.curves = []
        self.plot = 0

        _plotlaywout = QVBoxLayout()

        self.graphWidget = pg.PlotWidget()
        # self.graphWidget.setMinimumSize(800, 1000)
        self.graphWidget.setBackground('w')
        self.graphWidget.setLabels(bottom='Vds', left='Ids')
        self.graphWidget.addLegend()
        self.pen = pg.mkPen(color="black", width=3)
        self.graphWidget.showGrid(x=True, y=True)
        _plotlaywout.addWidget(self.graphWidget)
        self.setLayout(_plotlaywout)

    def newcurve(self, vgs):
        self.curves.append(self.graphWidget.plot([0], [0], name="Vgs = " + str(vgs)))
        self.i += 1
        self.plotline = self.curves[self.i]

    def plotdata(self, data):
        self.reset()
        for c in data:
            self.plotline = self.graphWidget.plot(c[1], c[2], pen=self.pen)
            self.newcurve(c[0])

    def plotlimits(self, power, v1, v2, plot):
        self.plot = plot
        if self.plot:
            x = np.linspace(int(v1), int(v2), 10)
            y = power / x
            self.maxPplotline = self.graphWidget.plot(x, y, pen=self.pen)
        else:
            self.maxPplotline.clear()
            self.maxPplotline.setData()

    def reset(self):
        self.curves = []
        self.i = -1
        self.graphWidget.clear()

    def smoothcurves(self, data, smooth):
        if smooth and len(data) >= 1:
            sdata = copy.deepcopy(data)
            for dat in sdata:
                xnew = np.linspace(min(dat[1]), max(dat[1]), 100)
                spl = make_interp_spline(dat[1], dat[2], 3)
                dat[2] = spl(xnew)
                dat[1] = xnew
            self.plotdata(sdata)
        else:
            self.plotdata(data)

