import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class plotwin(QWidget):
    def __init__(self):
        super().__init__()

        _plotlaywout = QVBoxLayout()
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.graphWidget.setLabels(bottom='Vds', left='Ids')
        self.graphWidget.addLegend()
        _plotlaywout.addWidget(self.graphWidget)
        self.graphWidget.showGrid(x=True, y=True)
        self.setLayout(_plotlaywout)

    def newcurve(self, Vgs):
        self.curves.append(self.graphWidget.plot([0], [0], name="Vgs = " + str(Vgs)))
        self.i += 1
        self.plotline = self.curves[self.i]

    def updateplot(self, data):
        self.reset()
        for c in data:
            print(c)
            self.plotline = self.graphWidget.plot(c[1], c[2])
            self.newcurve(c[0])

    def reset(self):
        self.curves = []
        self.i = -1
        self.graphWidget.clear()

