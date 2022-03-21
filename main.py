import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtWidgets, QtGui, QtCore, Qt
import glob
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Qt4Agg")
from matplotlib.backend_bases import NavigationToolbar2
from mode_viewer_gui import Ui_ModeViever
from cdm import read_comsol_table, get_file_ids  # Comsol Data Managing functions
import time
# import sys, os
# matplotlib.use("Qt4Agg")


# def resource_path(relative_path):
#     if hasattr(sys, '_MEIPASS'):
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)
def air(wl):
    return 1 + (0.05792105 / (238.0185 - 1 / wl ** 2)) + (0.00167917 / (57.362 - 1 / wl ** 2))


def from_wl_to_f(t, wl):
    return 2*t/wl * np.sqrt(glass(wl)**2-air(wl)**2)


def glass(wl):
    return np.sqrt(1 + (0.6961663 * wl ** 2) / (wl ** 2 - 0.0684043 ** 2) + (0.4079426 * wl ** 2) / (
                wl ** 2 - 0.1162414 ** 2) + (0.8974794 * wl ** 2) / (wl ** 2 - 9.896161 ** 2))


class NavigationToolbar_2(NavigationToolbar):
    def __init__(self, canvas, parent=None, list_of_removed_tools=None):
        super().__init__(canvas, parent)
        actions = self.findChildren(QtWidgets.QAction)
        for tool in list_of_removed_tools:
            for a in actions:
                if a.text() == tool:
                    self.removeAction(a)
                    break


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.parent = parent
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

    def click(self):
        pass


class MyWindow(QtWidgets.QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_ModeViever()
        self.ui.setupUi(self)
        # self.setFixedSize(self.size())
        self.setFont(QtGui.QFont('SansSerif', 8))  # set font for all lines in application
        Width = 1024
        Height = 728
        self.setMinimumSize(Width, Height)
        self.resize_alg((Width, Height))
        self.resized.connect(self.resizeFunction)

        self.ui.pushButton_open.clicked.connect(self.btn_openFileNameDialog)
        self.ui.pushButton_open_folder.clicked.connect(self.btn_openFolderWithTxts)

        self.settings = QtCore.QSettings("nope", "mb")
        self.last_opened_folder = self.settings.value("last_folder", "", type=str)
        self.filename = None
        self.filenames_all = None
        self.filename_without_path = None
        self.wls = None
        self.neffs = None
        self.CLm = None
        self.F = None

        self.wls_all = None
        self.neffs_all = None
        self.CLm_all = None
        self.F_all = None

        self.filenames = None
        self.filenames_without_path = []
        self.plot_files = None
        self.wls_list = []
        self.neffs_list = []
        self.CLm_list = []
        self.F_list = []

        self.wls_all_list = []
        self.neffs_all_list = []
        self.CLm_all_list = []
        self.F_all_list = []

        self.multi_plots = None
        self.plot_cl = self.ui.radioButton_plot_CL.isChecked()
        self.plot_neff = self.ui.radioButton_plot_neff.isChecked()
        self.plot_f = self.ui.radioButton_plot_F.isChecked()
        self.norm_freq = self.ui.checkBox_plot_x_in_norm_freq.isChecked()
        self.hide_not_rec = self.ui.checkBox_hide_not_recognized.isChecked()
        self.legend_bool = self.ui.checkBox_legend.isChecked()

        self.connect_bool_but_to_var(self.ui.radioButton_plot_CL, self.set_plot_cl)
        self.connect_bool_but_to_var(self.ui.radioButton_plot_neff, self.set_plot_neff)
        self.connect_bool_but_to_var(self.ui.radioButton_plot_F, self.set_plot_f)
        self.connect_bool_but_to_var(self.ui.checkBox_plot_x_in_norm_freq, self.set_norm_freq)
        self.connect_bool_but_to_var(self.ui.checkBox_hide_not_recognized, self.set_hide_not_rec)
        self.connect_bool_but_to_var(self.ui.checkBox_legend, self.set_legend_bool)

        self.thickness = 1.0

        self.ui.lineEdit_thickness_value.textChanged.connect(self.set_thickness)

        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.sc2 = MplCanvas(self, width=5, height=4, dpi=100)
        self.remove_tools = ["Back", "Forward", "Subplots", "Customize", "Save"]
        toolbar1 = NavigationToolbar_2(self.sc, self, self.remove_tools)
        toolbar2 = NavigationToolbar_2(self.sc2, self, self.remove_tools)

        self.init_graph(self.sc, self.ui.widget_graph, toolbar1)
        self.init_graph(self.sc2, self.ui.widget_graph_2, toolbar2)
        self.showMaximized()

        self.cid_field_multi_file = None
        self.cid_field_one_file = None
        ## reset limits
        self.sc.figure.canvas.mpl_connect('button_press_event', self.button_press)
        self.sc.figure.canvas.mpl_connect('button_release_event', self.button_release)
        self.current_x_axes_0 = None
        self.current_x_axes_1 = None
        self.current_y_axes_0 = None
        self.current_y_axes_1 = None
        self.base_limits = None
        toolbar1.actions()[0].triggered.connect(self.home_callback)

        self.model = QtGui.QStandardItemModel(self.ui.listView)
        self.ui.pushButton_replot_list.clicked.connect(self.reset_plot)
        # self.ui.listView.setWindowTitle('Example List')

    def reset_plot(self):
        if self.multi_plots:
            self.take_data_list()
            self.call_plot_data()
        else:
            self.call_plot_data()
            # self.reset_limits()

    def on_item_changed(self, item:QtGui.QStandardItem):
        # If the changed item is not checked, don't bother checking others
        if not item.checkState():
            # ind2 = self.model.indexFromItem(item)
            # print(item.text(), ind2.row())
            for file in self.filenames:
                if item.text() in file and file in self.filenames:
                    self.filenames.remove(file)
        else:
            # ind2 = self.model.indexFromItem(item)
            for file in self.filenames_all:
                if item.text() in file and file not in self.filenames:
                    self.filenames.append(file)

            # fnd = self.model.findItems(item.text())
            # fnd.

    def take_data_list(self):
        self.clean_lists()
        for file in self.filenames:
            sp = file.split("\\")

            self.take_data(file)

            self.filenames_without_path += [sp[len(sp) - 1].split(".")[0]]
            self.wls_list += [self.wls]
            self.neffs_list += [self.neffs]
            self.CLm_list += [self.CLm]
            self.F_list += [self.F]

            self.wls_all_list += [self.wls_all]
            self.neffs_all_list += [self.neffs_all]
            self.CLm_all_list += [self.CLm_all]
            self.F_all_list += [self.F_all]

    def reset_list_viewer(self, list_of_files):
        self.model.clear()
        for file in list_of_files:
            item = QtGui.QStandardItem(file)
            item.setCheckable(True)

            item.setCheckState(QtCore.Qt.Checked)
            print(item.checkState())
            self.model.appendRow(item)

        self.ui.listView.setModel(self.model)
        self.ui.listView.show()
        self.model.itemChanged.connect(self.on_item_changed)

    def reset_limits_norm_freq(self, value):
        list0 = [self.current_x_axes_0, self.current_x_axes_0, self.current_y_axes_0, self.current_y_axes_1]

        if self.base_limits is not None and all(elem is not None for elem in list0):
            x_0, x_1 = self.base_limits[0]
            const_norm_freq = 2 * self.thickness * (1.45 ** 2 - 1) ** 0.5
            if value:
                x_0 = const_norm_freq / (x_0 * 1e-3)
                x_1 = const_norm_freq / (x_1 * 1e-3)
                # x_0 = from_wl_to_f(self.thickness, (x_0 * 1e-3))
                # x_1 = from_wl_to_f(self.thickness, (x_1 * 1e-3))
                x_0, x_1 = x_1, x_0
                self.current_x_axes_0 = const_norm_freq / (self.current_x_axes_0 * 1e-3)
                self.current_x_axes_1 = const_norm_freq / (self.current_x_axes_1 * 1e-3)
                self.current_x_axes_1, self.current_x_axes_0 = self.current_x_axes_0, self.current_x_axes_1
            else:
                x_0 = (x_0 / const_norm_freq) ** -1 * 1e3
                x_1 = (x_1 / const_norm_freq) ** -1 * 1e3
                x_0, x_1 = x_1, x_0
                self.current_x_axes_0 = (self.current_x_axes_0 / const_norm_freq) ** -1 * 1e3
                self.current_x_axes_1 = (self.current_x_axes_1 / const_norm_freq) ** -1 * 1e3
                self.current_x_axes_1, self.current_x_axes_0 = self.current_x_axes_0, self.current_x_axes_1
            self.base_limits[0] = x_0, x_1
            self.sc.axes.set_xlim(self.current_x_axes_0, self.current_x_axes_1)
            self.sc.axes.set_ylim(self.current_y_axes_0, self.current_y_axes_1)
            self.sc.draw()

    def reset_limits(self):
        if self.base_limits is not None:
            self.base_limits = None
        self.base_limits = [self.sc.axes.get_xlim(), self.sc.axes.get_ylim()]
        self.current_x_axes_0, self.current_x_axes_1 = self.base_limits[0]
        self.current_y_axes_0, self.current_y_axes_1 = self.base_limits[1]

    def home_callback(self):
        print("home called")
        if self.base_limits is not None:
            self.sc.axes.set_xlim(self.base_limits[0])
            self.sc.axes.set_ylim(self.base_limits[1])
            self.current_x_axes_0, self.current_x_axes_1 = self.base_limits[0]
            self.current_y_axes_0, self.current_y_axes_1 = self.base_limits[1]

    def button_release(self, event):

        if self.sc.toolbar.mode == "zoom rect":
            self.current_x_axes_1 = event.xdata
            self.current_y_axes_1 = event.ydata
            x_0 = self.current_x_axes_0 if self.current_x_axes_0 < self.current_x_axes_1 else self.current_x_axes_1
            x_1 = self.current_x_axes_1 if self.current_x_axes_0 < self.current_x_axes_1 else self.current_x_axes_0
            y_0 = self.current_y_axes_0 if self.current_y_axes_0 < self.current_y_axes_1 else self.current_y_axes_1
            y_1 = self.current_y_axes_1 if self.current_y_axes_0 < self.current_y_axes_1 else self.current_y_axes_0
            self.current_x_axes_0, self.current_x_axes_1 = x_0, x_1
            self.current_y_axes_0, self.current_y_axes_1 = y_0, y_1
            self.sc.axes.set_xlim(x_0, x_1)
            self.sc.axes.set_ylim(y_0, y_1)
        if self.sc.toolbar.mode == "pan/zoom":
            print([self.sc.axes.get_xlim(), self.sc.axes.get_ylim()])
            x_0, x_1 = self.sc.axes.get_xlim()
            y_0, y_1 = self.sc.axes.get_ylim()
            self.current_x_axes_0, self.current_x_axes_1 = x_0, x_1
            self.current_y_axes_0, self.current_y_axes_1 = y_0, y_1
            self.sc.axes.set_xlim(x_0, x_1)
            self.sc.axes.set_ylim(y_0, y_1)

    def button_press(self, event):
        if self.sc.toolbar.mode == "zoom rect":
            self.current_x_axes_0 = event.xdata
            self.current_y_axes_0 = event.ydata

    def clean_lists(self):
        self.filenames_without_path = []
        self.wls_list = []
        self.neffs_list = []
        self.CLm_list = []
        self.F_list = []

        self.wls_all_list = []
        self.neffs_all_list = []
        self.CLm_all_list = []
        self.F_all_list = []

    def click(self, event):
        start = time.time()
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        points = tuple(zip(xdata[ind], ydata[ind]))  # taken a point(s) under the arrow
        if len(points) == 1:
            if self.multi_plots:
                self.plot_field_from_list(ydata[ind], xdata[ind])
            else:
                self.plot_field(ydata[ind], xdata[ind])
            if self.base_limits != [(self.current_x_axes_0, self.current_x_axes_1),
                                    (self.current_y_axes_0, self.current_y_axes_1)]:
                self.sc.axes.set_xlim(self.current_x_axes_0, self.current_x_axes_1)
                self.sc.axes.set_ylim(self.current_y_axes_0, self.current_y_axes_1)
                self.sc.draw()
        print(f"time click={time.time()-start:0.3f}")

    # @staticmethod
    def init_graph(self, canvas, widget, toolbar):
        canvas.figure.tight_layout()
        if canvas == self.sc:
            canvas.figure.subplots_adjust(top=0.98,
                                          bottom=0.08,
                                          left=0.08,
                                          right=0.98,
                                          hspace=0.06,
                                          wspace=0.06
                                          )
        else:
            canvas.figure.subplots_adjust(top=0.92,
                                          bottom=0,
                                          left=0,
                                          right=1,
                                          hspace=0.06,
                                          wspace=0.06
                                          )

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        canvas.axes.autoscale(False)

    def plot_field_from_list(self, y_data, x_data):
        field_id = None
        # x_label_field = ""
        # path = ""
        for ind, filename in enumerate(self.filenames):
            if self.plot_cl:
                field_id = np.where(self.CLm_all_list[ind] == y_data)
            if self.plot_neff:
                field_id = np.where(self.neffs_all_list[ind] == y_data)
            if self.plot_f:
                field_id = np.where(self.F_all_list[ind] == y_data)

            if len(field_id[0]):
                field_id = field_id[0][0]
                if self.norm_freq:
                    const_norm_freq = 2 * self.thickness * (1.45 ** 2 - 1) ** 0.5
                    x = const_norm_freq / (self.wls_all_list[ind][field_id] * 1e6)
                    x_label_field = f'F={x:0.3f} '
                else:
                    x = self.wls_all_list[ind][field_id] * 1e9
                    x_label_field = f'wl={x:0.1f} [nm] '

                self.sc.axes.clear()
                self.call_plot_data()
                self.sc.axes.plot(x_data, y_data, "o", color="r", ms=5, picker=True)
                self.sc.draw()
                path = filename.split("\\")
                path = '\\'.join(path[0:len(path) - 1])
                path = f"{path}\\*.png"
                pics = glob.glob(path)
                try:
                    img = mpimg.imread(pics[field_id])
                except:
                    print("No image yet")
                    self.sc2.axes.set_title(f'There is no image for this mode yet')
                    self.sc2.draw()
                else:

                    self.sc2.axes.clear()
                    self.sc2.axes.set_axis_off()
                    self.sc2.axes.imshow(img)
                    self.sc2.axes.set_title(f'{x_label_field}'  # f'neff={self.neffs_all[field_id]:0.15f}\n'
                                            f'CL={self.CLm_all_list[ind][field_id]:0.3f} [dB/km]')
                    self.sc2.draw()
                ## plot on label
                # pix = QtGui.QPixmap(pics[field_id])
                # self.ui.label_field.setPixmap(pix)
                break

    def plot_field(self, y_data, x_data):
        field_id = None
        if self.plot_cl:
            field_id = np.where(self.CLm_all == y_data)[0][0]
        if self.plot_neff:
            field_id = np.where(self.neffs_all == y_data)[0][0]
        if self.plot_f:
            field_id = np.where(self.F_all == y_data)[0][0]
        # x_label_field = ""
        if self.norm_freq:
            const_norm_freq = 2 * self.thickness * (1.45 ** 2 - 1) ** 0.5
            x = const_norm_freq / (self.wls_all[field_id] * 1e6)
            x_label_field = f'F={x:0.3f}'
        else:
            x = self.wls_all[field_id] * 1e9
            x_label_field = f'wl={x:0.1f} [nm]'
        self.sc.axes.clear()
        self.call_plot_data()
        self.sc.axes.plot(x_data, y_data, "o", color="r", ms=5, picker=True)
        self.sc.draw()
        path = self.last_opened_folder
        path = f"{path}\\*.png"
        pics = glob.glob(path)
        try:
            img = mpimg.imread(pics[field_id])  ####################### NO FILE
            print(f"Picture: {pics[field_id]}")
        except:
            print("No image yet")
            self.sc2.axes.set_title(f'There is no image for this mode yet')
            self.sc2.draw()
        else:
            self.sc2.axes.clear()
            self.sc2.axes.set_axis_off()
            self.sc2.axes.imshow(img)
            self.sc2.axes.set_title(f'{x_label_field} CL={self.CLm_all[field_id]:0.3f} [dB/km]')
            self.sc2.draw()
        ## plot on label
        # pix = QtGui.QPixmap(pics[field_id])
        # self.ui.label_field.setPixmap(pix)

    def set_thickness(self):
        text = self.ui.lineEdit_thickness_value.text()
        try:
            self.thickness = float(text)
            if self.norm_freq:
                self.call_plot_data()
                self.reset_limits()
        except:
            print("value error")

    @staticmethod
    def connect_bool_but_to_var(bool_button, setter):
        bool_button.clicked.connect(lambda: (setter(bool_button.isChecked())))

    def set_plot_cl(self, value):
        self.plot_cl = value
        self.plot_neff = not value
        self.plot_f = not value
        self.call_plot_data()
        self.reset_limits()
        # self.reset_limits_norm_freq(self.norm_freq)

    def set_plot_neff(self, value):
        self.plot_neff = value
        self.plot_cl = not value
        self.plot_f = not value
        self.call_plot_data()
        self.reset_limits()
        # self.reset_limits_norm_freq(self.norm_freq)

    def set_plot_f(self, value):
        self.plot_f = value
        self.plot_cl = not value
        self.plot_neff = not value
        self.call_plot_data()
        self.reset_limits()
        # self.reset_limits_norm_freq(self.norm_freq)

    def set_norm_freq(self, value):
        self.norm_freq = value
        self.call_plot_data()
        self.reset_limits_norm_freq(self.norm_freq)

    def set_legend_bool(self, value):
        self.legend_bool = value
        self.call_plot_data()
        # self.reset_limits()

    def set_hide_not_rec(self, value):
        self.hide_not_rec = value
        self.call_plot_data()
        self.reset_limits()
        # self.reset_limits_norm_freq(self.norm_freq)

    def call_plot_data(self):
        if not self.multi_plots:
            if self.filename is None:
                return
            self.plot_data()
        elif self.multi_plots:
            if self.filenames is None:
                return
            self.plot_data_list()
        else:
            pass

    def plot_data_list(self):
        #### Considering same glass thickness for all the files
        self.sc.axes.cla()
        for ind, filename in enumerate(self.filenames_without_path):
            # print(filename)
            x_all = None
            y_all = None
            x = None
            y = None
            y_label = ""

            if self.plot_cl:
                x_all, y_all = self.wls_all_list[ind] * 1e9, self.CLm_all_list[ind]
                x, y = self.wls_list[ind] * 1e9, self.CLm_list[ind]
                y_label = "Confinement loss [dB/km]"
            elif self.plot_neff:
                x_all, y_all = self.wls_all_list[ind] * 1e9, self.neffs_all_list[ind]
                x, y = self.wls_list[ind] * 1e9, self.neffs_list[ind]
                y_label = "Effective index"
            elif self.plot_f:
                x, y = self.wls_list[ind] * 1e9, self.F_list[ind]
                y_label = "Optical Overlap F"
            # x_label = ""
            if self.norm_freq:
                x_label = "Normalized Frequency"
                const_norm_freq = 2 * self.thickness * (1.45 ** 2 - 1) ** 0.5
                x = const_norm_freq / (x * 1e-3)
                # x = from_wl_to_f(self.thickness, (x * 1e-3))
                if not self.hide_not_rec and not self.plot_f:
                    x_all = const_norm_freq / (x_all * 1e-3)
                    # x_all = from_wl_to_f(self.thickness, (x_all * 1e-3))
            else:
                x_label = "Wavelength [nm]"

            if not self.hide_not_rec and (self.plot_cl or self.plot_neff):
                self.sc.axes.plot(x_all, y_all, "o", lw=1., ms=2, label=f"All the modes {filename}", picker=True)
            self.sc.axes.plot(x, y, "o-", lw=1., ms=2, label=f"Recognized {filename}", picker=True)
            self.sc.axes.set_ylabel(y_label)
            self.sc.axes.set_xlabel(x_label)
        if self.legend_bool:
            self.sc.axes.legend(title=f"")
        if self.plot_cl or self.plot_f:
            self.sc.axes.set_yscale('log')
        elif self.plot_neff:
            self.sc.axes.set_yscale('linear')
        self.sc.axes.grid(which="both")
        self.sc.axes.minorticks_on()
        self.sc.draw()

    def plot_data(self):

        x_all = None
        y_all = None
        x = None
        y = None
        y_label = ""

        if self.plot_cl:
            x_all, y_all = self.wls_all * 1e9, self.CLm_all
            x, y = self.wls * 1e9, self.CLm
            y_label = "Confinement loss [dB/km]"
        elif self.plot_neff:
            x_all, y_all = self.wls_all * 1e9, self.neffs_all
            x, y = self.wls * 1e9, self.neffs
            y_label = "Effective index"
        elif self.plot_f:
            x, y = self.wls * 1e9, self.F
            y_label = "Optical Overlap F"
        # x_label = ""
        if self.norm_freq:
            x_label = "Normalized Frequency"
            const_norm_freq = 2 * self.thickness * (1.45 ** 2 - 1) ** 0.5
            x = const_norm_freq / (x * 1e-3)
            # x = from_wl_to_f(self.thickness, (x * 1e-3))
            if not self.hide_not_rec and not self.plot_f:
                x_all = const_norm_freq / (x_all * 1e-3)
                # x_all = from_wl_to_f(self.thickness, (x_all * 1e-3))
        else:
            x_label = "Wavelength [nm]"

        self.sc.axes.cla()
        if not self.hide_not_rec and (self.plot_cl or self.plot_neff):
            self.sc.axes.plot(x_all, y_all, "o", color="b", lw=1., ms=2, label="All the modes", picker=True)
        self.sc.axes.plot(x, y, "o-", color="g", lw=1., ms=2, label="Recognized", picker=True)
        self.sc.axes.set_ylabel(y_label)
        self.sc.axes.set_xlabel(x_label)
        if self.legend_bool:
            self.sc.axes.legend(title=f"{self.filename_without_path}")
        if self.plot_cl or self.plot_f:
            self.sc.axes.set_yscale('log')
        elif self.plot_neff:
            self.sc.axes.set_yscale('linear')
        self.sc.axes.grid(which="both")
        self.sc.axes.minorticks_on()

        self.sc.draw()

    def take_data(self, file):
        table_temp = read_comsol_table(file)
        table_temp = table_temp[:, 0:8]
        table_temp_all = table_temp
        # table.append(table_temp)
        table_temp = table_temp[~np.isnan(table_temp).any(axis=1)]  # removing all the NaN lines
        self.wls = np.real(table_temp[:, 0])
        self.neffs = np.real(table_temp[:, 1])
        self.CLm = np.real(table_temp[:, 3])
        self.F = np.real(table_temp[:, 5])

        self.wls_all = np.real(table_temp_all[:, 0])
        self.neffs_all = np.real(table_temp_all[:, 1])
        self.CLm_all = np.real(table_temp_all[:, 2])
        self.F_all = np.real(table_temp_all[:, 5])

    def btn_openFileNameDialog(self):
        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open solution txt", self.last_opened_folder,
                                                  "Txt Files (*.txt)")
        if fileName:
            sp = fileName.split("/")
            folder = sp[0:len(sp) - 1]
            self.last_opened_folder = "/".join(folder)
            self.settings.setValue("last_folder", self.last_opened_folder)
            self.settings.sync()
            print(self.last_opened_folder)
            self.filename = fileName
            self.filename_without_path = sp[len(sp) - 1].split(".")[0]
            self.take_data(self.filename)

            self.multi_plots = False
            self.cid_field_one_file = self.sc.figure.canvas.mpl_connect('pick_event', self.click)  # !!
            self.call_plot_data()
            self.reset_limits()

    def btn_openFolderWithTxts(self):
        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        # files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
        #                                         "Text files (*.txt)", options=options)
        #        return files
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.filenames = glob.glob(f'{folder}/**/*.txt', recursive=True)
            self.filenames_all = self.filenames.copy()
            # print(*self.filenames, sep="\n")
            self.take_data_list()
            self.reset_list_viewer(self.filenames_without_path)
            self.multi_plots = True
            self.cid_field_multi_file = self.sc.figure.canvas.mpl_connect('pick_event', self.click)  # !!
            self.call_plot_data()
            self.reset_limits()

    def resize_alg(self, window_geom):
        W, H = window_geom
        tw_of_th = int(2 * W / 3)
        on_of_th = int(1 * W / 3)
        half_of_h = int(H / 2)
        bot_line = H - 5
        self.ui.groupBox.setGeometry(10, 0, tw_of_th, bot_line)
        self.ui.groupBox_2.setGeometry(tw_of_th + 20, half_of_h - 5, on_of_th - 30, half_of_h)
        self.ui.groupBox_3.setGeometry(tw_of_th + 20, 0, on_of_th - 30, half_of_h - 10)

        self.ui.widget_graph.setGeometry(0, 0, tw_of_th, bot_line)
        self.ui.widget_graph_2.setGeometry(0, 10, on_of_th - 30, half_of_h - 10)
        # self.ui.label_field.setGeometry(0, 10, on_of_th - 30, half_of_h - 10)

    def resizeEvent(self, event):
        self.resized.emit()
        return super(MyWindow, self).resizeEvent(event)

    def resizeFunction(self):
        geom = (self.geometry().width(), self.geometry().height())
        self.resize_alg(geom)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = MyWindow()
    application.show()
    sys.exit(app.exec())
