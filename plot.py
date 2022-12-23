import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class plotwin(QWidget):
    def __init__(self):
        super().__init__()

        _plotlaywout = QVBoxLayout()

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.graphWidget.setLabels(bottom='Vds', left='Ids')
        _plotlaywout.addWidget(self.graphWidget)
        self.graphWidget.showGrid(x=True, y=True)
        self.setLayout(_plotlaywout)
        self.plotline = self.graphWidget.plot([0], [0])

    def updateplot(self, data):
        print(data)
        self.plotline = self.graphWidget.plot(data[1], data[2])
