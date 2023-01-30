from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QVBoxLayout, QHBoxLayout, QFileDialog

from plot import PlotWin


class MatchWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.curves = {}
        match_layout = QVBoxLayout()
        horiz1_layout = QHBoxLayout()
        ver1_layout = QVBoxLayout()

        self.curves_list_lstwidget = QListWidget()
        self.curves_list_lstwidget.setSelectionMode(QListWidget.MultiSelection)
        self.curves_list_lstwidget.itemSelectionChanged.connect(self.plot_curves)
        horiz1_layout.addWidget(self.curves_list_lstwidget)

        load_curve_button = QPushButton("Load curve")
        load_curve_button.pressed.connect(self.load_curve)
        delete_curve_button = QPushButton("Delete curve")
        delete_curve_button.pressed.connect(self.delete_curve)
        ver1_layout.addWidget(load_curve_button)
        ver1_layout.addWidget(delete_curve_button)
        horiz1_layout.addLayout(ver1_layout)
        match_layout.addLayout(horiz1_layout)

        self.match_plot_area = PlotWin()
        match_layout.addWidget(self.match_plot_area)

        self.setLayout(match_layout)

    def load_curve(self):
        load_file = QFileDialog.getOpenFileName()[0]
        with open(load_file, mode='r') as file:
            lines = file.read()
            d = eval(lines)
            self.curves[load_file] = d
            self.curves_list_lstwidget.addItem(load_file)
            self.plot_curves()

    def plot_curves(self):
        self.match_plot_area.reset()
        for c in self.curves_list_lstwidget.selectedItems():
            self.match_plot_area.plotdata(self.curves[c.text()], False)

    def delete_curve(self):
        for selected in self.curves_list_lstwidget.selectedItems():
            del self.curves[selected.text()]
        for x in self.curves_list_lstwidget.selectedIndexes():
            self.curves_list_lstwidget.takeItem(x.row())




