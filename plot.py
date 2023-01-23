import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from scipy.interpolate import make_interp_spline
import copy


class PlotWin(QWidget):
    def __init__(self):
        super().__init__()

        self.plotline = []
        self.curves = {}
        self.plot = 0
        self.i = -1

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

    # def newcurve(self, vgs):
    #     self.curves[vgs] = self.graphWidget.plot([0], [0], name="Vgs = " + str(vgs))

    def plotdata(self, data):
        self.reset()
        for c in data.keys():
            self.plotline = self.graphWidget.plot(data[c][0], data[c][1], pen=self.pen)

    def plotlimits(self, power, v1, v2, plot):
        self.plot = plot
        if self.plot:
            x = np.linspace(int(v1), int(v2), 10)
            y = power / x
            self.maxPplotline = self.graphWidget.plot(x, y, pen=self.pen)
        else:
            self.maxPplotline.clear()
            self.maxPplotline.setData()

    def smoothcurves(self, data, smooth):
        if smooth and len(data) >= 1:
            sdata = copy.deepcopy(data)
            for dat in sdata.keys():
                xnew = np.linspace(min(sdata[dat][0]), max(sdata[dat][0]), 100)
                spl = make_interp_spline(sdata[dat][0], sdata[dat][1], 3)
                sdata[dat][1] = spl(xnew)
                sdata[dat][0] = xnew
            self.plotdata(sdata)
        else:
            self.plotdata(data)

    def reset(self):
        self.curves = []
        self.i = -1
        self.graphWidget.clear()
