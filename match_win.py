from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel

from plot import PlotWin


class MatchWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.curves = {}
        self.colors = ["b", "r", "g", "c", "m", "y", "k"]
        self.color_count = 0

        match_layout = QVBoxLayout()
        horiz1_layout = QHBoxLayout()
        ver1_layout = QVBoxLayout()

        self.curves_list_lstwidget = QListWidget()
        self.curves_list_lstwidget.setFixedHeight(200)
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

    def color_pick(self):
        if self.color_count >= len(self.colors):
            self.color_count = 0
            print(self.color_count)
        colorchoise = self.colors[self.color_count]
        self.color_count += 1
        return colorchoise

    def load_curve(self):
        file_list = QFileDialog.getOpenFileNames()[0]
        for load_file in file_list:
            with open(load_file, mode='r') as file:
                lines = file.read()
                color = self.color_pick()
                self.curves[load_file] = [eval(lines), color]
                self.curves_list_lstwidget.addItem(load_file)
                self.plot_curves()

    def plot_curves(self):
        self.match_plot_area.reset()
        for dut in self.curves_list_lstwidget.selectedItems():
            self.match_plot_area.plotdata(self.curves[dut.text()][0], False, dut.text(), self.curves[dut.text()][1])

    def delete_curve(self):
        for selected in self.curves_list_lstwidget.selectedItems():
            del self.curves[selected.text()]
        for x in self.curves_list_lstwidget.selectedIndexes():
            self.curves_list_lstwidget.takeItem(x.row())




