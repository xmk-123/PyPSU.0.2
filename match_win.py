import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, \
    QMessageBox, QAbstractItemView, QListView, QFrame, QSizePolicy

from plot import PlotWin
import similaritymeasures
from PyQt5.QtCore import Qt


class MatchWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.curves = {}
        self.colors = ["b", "r", "g", "c", "m", "y", "k"]
        self.color_count = 0

        match_layout = QVBoxLayout()
        self.setLayout(match_layout)

        horiz1_layout = QHBoxLayout()
        ver1_layout = QVBoxLayout()
        base_set_layout = QHBoxLayout()
        qtfy_PCM_layout = QHBoxLayout()
        qtfy_Frechet_layout = QHBoxLayout()
        qtfy_area_layout = QHBoxLayout()
        qtfy_PLength_layout = QHBoxLayout()
        qtfy_Dynamic_layout = QHBoxLayout()
        qtfy_absolute_layout = QHBoxLayout()
        qtfy_squared_layout = QHBoxLayout()
        qtfy_mine_Vlayout = QVBoxLayout()
        qtfy_mine_Hlayout = QHBoxLayout()

        self.curves_list_lstwidget = QListWidget()
        self.curves_list_lstwidget.setFixedHeight(200)
        self.curves_list_lstwidget.setSelectionMode(QListWidget.MultiSelection)
        self.curves_list_lstwidget.itemSelectionChanged.connect(self.plot_curves)
        horiz1_layout.addWidget(self.curves_list_lstwidget)

        load_curve_button = QPushButton("Load curve")
        load_curve_button.pressed.connect(self.load_curve)
        delete_curve_button = QPushButton("Delete curve")
        delete_curve_button.pressed.connect(self.delete_curve)
        set_base_curve_button = QPushButton("Set base curve")
        set_base_curve_button.pressed.connect(self.base_curve)
        ver1_layout.addWidget(load_curve_button)
        ver1_layout.addWidget(delete_curve_button)
        ver1_layout.addWidget(set_base_curve_button)
        horiz1_layout.addLayout(ver1_layout)
        match_layout.addLayout(horiz1_layout)

        self.match_plot_area = PlotWin()
        match_layout.addWidget(self.match_plot_area)

        self.qtfy_button = QPushButton("quantify")
        self.qtfy_button.pressed.connect(self.quantify)
        match_layout.addWidget(self.qtfy_button)

        _base_set_label = QLabel("Base Set of curves")
        match_layout.addWidget(_base_set_label)
        self.base_set = QLabel("None")
        self.base_set.setFixedHeight(50)
        _clear_base_button = QPushButton("Clear base set")
        _clear_base_button.pressed.connect(self.clear_base)
        base_set_layout.addWidget(self.base_set)
        base_set_layout.addWidget(_clear_base_button)
        match_layout.addLayout(base_set_layout)

        separator_3 = QFrame()
        separator_3.setFrameShape(QFrame.HLine)
        separator_3.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator_3.setLineWidth(5)

        match_layout.addWidget(separator_3)

        self.qtfy_PCM_label = QLabel("PCM")
        self.qtfy_PCM_Value = QLabel()
        qtfy_PCM_layout.addWidget(self.qtfy_PCM_label)
        qtfy_PCM_layout.addWidget(self.qtfy_PCM_Value)
        match_layout.addLayout(qtfy_PCM_layout)

        self.qtfy_Frechet_label = QLabel("Frechet")
        self.qtfy_Frechet_Value = QLabel()
        qtfy_Frechet_layout.addWidget(self.qtfy_Frechet_label)
        qtfy_Frechet_layout.addWidget(self.qtfy_Frechet_Value)
        match_layout.addLayout(qtfy_Frechet_layout)

        self.qtfy_area_label = QLabel("area")
        self.qtfy_area_Value = QLabel()
        qtfy_area_layout.addWidget(self.qtfy_area_label)
        qtfy_area_layout.addWidget(self.qtfy_area_Value)
        match_layout.addLayout(qtfy_area_layout)

        self.qtfy_PLength_label = QLabel("PLength")
        self.qtfy_PLength_Value = QLabel()
        qtfy_PLength_layout.addWidget(self.qtfy_PLength_label)
        qtfy_PLength_layout.addWidget(self.qtfy_PLength_Value)
        match_layout.addLayout(qtfy_PLength_layout)

        self.qtfy_Dynamic_label = QLabel("Dynamic")
        self.qtfy_Dynamic_Value = QLabel()
        qtfy_Dynamic_layout.addWidget(self.qtfy_Dynamic_label)
        qtfy_Dynamic_layout.addWidget(self.qtfy_Dynamic_Value)
        match_layout.addLayout(qtfy_Dynamic_layout)

        self.qtfy_absolute_label = QLabel("absolute")
        self.qtfy_absolute_Value = QLabel()
        qtfy_absolute_layout.addWidget(self.qtfy_absolute_label)
        qtfy_absolute_layout.addWidget(self.qtfy_absolute_Value)
        match_layout.addLayout(qtfy_absolute_layout)

        self.qtfy_squared_label = QLabel("squared")
        self.qtfy_squared_Value = QLabel()
        qtfy_squared_layout.addWidget(self.qtfy_squared_label)
        qtfy_squared_layout.addWidget(self.qtfy_squared_Value)
        match_layout.addLayout(qtfy_squared_layout)

        self.qtfy_mine_label = QLabel("mine")
        self.qtfy_mine_Value = QLabel()
        qtfy_mine_Hlayout.addWidget(self.qtfy_mine_label)
        qtfy_mine_Hlayout.addWidget(self.qtfy_mine_Value)
        qtfy_mine_Vlayout.addLayout(qtfy_mine_Hlayout)
        self.qtfy_mine_message = QLabel()
        self.qtfy_mine_message.setStyleSheet("color: red")
        qtfy_mine_Vlayout.addWidget(self.qtfy_mine_message)

        match_layout.addLayout(qtfy_mine_Vlayout)

    def convert_to_2D_np_array(self, _data):
        _np_2d_array = np.zeros((len(_data[0]), 2))
        _np_2d_array[:, 0] = _data[0]
        _np_2d_array[:, 1] = _data[1]
        return _np_2d_array

    def clear_base(self):
        self.curves_list_lstwidget.addItem(self.base_set.text())
        self.base_set.setText("None")
        self.plot_curves()

    def base_curve(self):
        if len(self.curves_list_lstwidget.selectedItems()) == 1:
            self.base_set.setText(self.curves_list_lstwidget.selectedItems()[0].text())
            self.curves_list_lstwidget.takeItem(self.curves_list_lstwidget.currentRow())
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("Select 1 set of curves for base")
            msg.setInformativeText("")
            msg.setWindowTitle("More than 1 set selected")
            msg.setDetailedText("")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def quantify(self):
        self.qtfy_mine_Value.clear()
        self.qtfy_mine_message.clear()
        self.qtfy_PCM_Value.clear()
        self.qtfy_Frechet_Value.clear()
        self.qtfy_area_Value.clear()
        self.qtfy_PLength_Value.clear()
        self.qtfy_Dynamic_Value.clear()
        self.qtfy_absolute_Value.clear()
        self.qtfy_squared_Value.clear()

        if len(self.curves_list_lstwidget.selectedItems()) == 1 and self.base_set.text() != "None":
            print(self.base_set.text())
            base_data = self.curves[self.base_set.text()][0]
            comp_data = self.curves[self.curves_list_lstwidget.selectedItems()[0].text()][0]

            if base_data.keys() == comp_data.keys():
                mine = self.my_qtfy_method(base_data, comp_data)
                self.qtfy_mine_Value.setText(str(mine))
                pcm = df = area = cl = dtw = mae = mse = 0
                for (base_vgs, comp_vgs) in zip(base_data.keys(), comp_data.keys()):
                    base = self.convert_to_2D_np_array(base_data[base_vgs][:2])
                    comp = self.convert_to_2D_np_array(comp_data[comp_vgs][:2])

                    pcm += similaritymeasures.pcm(base, comp)
                    df += similaritymeasures.frechet_dist(base, comp)
                    area += similaritymeasures.area_between_two_curves(base, comp)
                    cl += similaritymeasures.curve_length_measure(base, comp)
                    dtw += similaritymeasures.dtw(base, comp)[0]

                    try:
                        mae += similaritymeasures.mae(base, comp)
                    except BaseException as e:
                        print(e)
                    try:
                        mse += similaritymeasures.mse(base, comp)
                    except BaseException as e:
                        print(e)
                    # print("base Vgs : " + str(base_vgs) + "pcm : " + str(pcm))

                # quantify the difference between the two curves using PCM
                self.qtfy_PCM_Value.setText(str(pcm))
                # Discrete Frechet distance
                self.qtfy_Frechet_Value.setText(str(df))
                # area between two curves
                self.qtfy_area_Value.setText(str(area))
                # Curve Length based similarity measure
                self.qtfy_PLength_Value.setText(str(cl))
                # Dynamic Time Warping distance
                self.qtfy_Dynamic_Value.setText(str(dtw))
                # mean absolute error
                self.qtfy_absolute_Value.setText(str(mae))
                # mean squared error
                self.qtfy_squared_Value.setText(str(mse))

            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)

                msg.setText("****Devices' curves have different Vgs")
                msg.setInformativeText("")
                msg.setWindowTitle("Error Vgs data mismatch ")
                msg.setDetailedText("")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("A base set and one more set of curves must be selected")
            msg.setInformativeText("Drag and drop a set of curves from the list , into the base set of curves box, then select one curve from the curves list on top")
            msg.setWindowTitle("Error number of set of curves selected")
            msg.setDetailedText("")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def my_qtfy_method(self, base_curves, comp_curves):
        diff = 0
        message = ""
        for (base_vgs, comp_vgs) in zip(base_curves.keys(), comp_curves.keys()):
            base_data = base_curves[base_vgs][:2]
            comp_data = comp_curves[comp_vgs][:2]
            if base_data[0] != comp_data[0]:
                for i in range(min(len(base_data[0]), len(comp_data[0]))):
                    if base_data[0][i] != comp_data[0][i]:
                        base_data[0] = base_data[0][:i]
                        base_data[1] = base_data[1][:i]
                        comp_data[0] = comp_data[0][:i]
                        comp_data[1] = comp_data[1][:i]
                        break
                if i < 2:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Devices' curves have different Vds")
                    msg.setInformativeText("")
                    msg.setWindowTitle("Error Vds data mismatch")
                    msg.setDetailedText("")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec()
                    return "error"
                else:
                    message = self.qtfy_mine_message.text() + "Curves for Vgs=" + str(
                        base_vgs) + " had matching Vds up to " + str(base_data[0][-1]) + "V \n"
                    self.qtfy_mine_message.setText(message)

                # new_base_data = [[], []]
                # new_comp_data = [[], []]
                # for (base_vds, base_id) in zip(base_data[0], base_data[1]):
                #     for (comp_vds, comp_id) in zip(comp_data[0], comp_data[1]):
                #         print(base_vds, comp_vds)
                #         print(base_vds == comp_vds)
                #         if base_vds == comp_vds:
                #             new_base_data[0].append(base_vds)
                #             new_base_data[1].append(base_id)
                #             new_comp_data[0].append(comp_vds)
                #             new_comp_data[1].append(comp_id)
                #             break
                #         elif base_vds < comp_vds:
                #             msg = QMessageBox()
                #             msg.setIcon(QMessageBox.Information)
                #             msg.setText("Devices' curves have different Vds")
                #             msg.setInformativeText("")
                #             msg.setWindowTitle("Error Vds data mismatch")
                #             msg.setDetailedText("")
                #             msg.setStandardButtons(QMessageBox.Ok)
                #             msg.exec()
                #             return "error"
                # base_data = new_base_data
                # comp_data = new_comp_data
                # message = self.qtfy_mine_message.text() + "Curves for Vgs=" + str(base_vgs) + " had matching Vds up to " + str(base_data[0][-1]) + "V \n"
                # self.qtfy_mine_message.setText(message)

            for (a, b) in zip(base_data[1], comp_data[1]):
                diff += abs(a - b)
        return diff

    def color_pick(self):
        if self.color_count >= len(self.colors):
            self.color_count = 0
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
        if self.base_set.text() != "None":
            self.match_plot_area.plotdata(self.curves[self.base_set.text()][0], False, self.base_set.text(), self.curves[self.base_set.text()][1])

    def delete_curve(self):
        for selected in self.curves_list_lstwidget.selectedItems():
            del self.curves[selected.text()]
        for x in self.curves_list_lstwidget.selectedIndexes():
            self.curves_list_lstwidget.takeItem(x.row())
