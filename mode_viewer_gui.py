# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mode_viewer_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ModeViever(object):
    def setupUi(self, ModeViever):
        ModeViever.setObjectName("ModeViever")
        ModeViever.resize(1217, 662)
        self.centralwidget = QtWidgets.QWidget(ModeViever)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 651, 451))
        self.groupBox.setObjectName("groupBox")
        self.widget_graph = QtWidgets.QWidget(self.groupBox)
        self.widget_graph.setGeometry(QtCore.QRect(10, 20, 631, 421))
        self.widget_graph.setObjectName("widget_graph")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(660, 370, 321, 281))
        self.groupBox_2.setObjectName("groupBox_2")
        self.widget_graph_2 = QtWidgets.QWidget(self.groupBox_2)
        self.widget_graph_2.setGeometry(QtCore.QRect(10, 170, 301, 101))
        self.widget_graph_2.setObjectName("widget_graph_2")
        self.label_field = QtWidgets.QLabel(self.groupBox_2)
        self.label_field.setGeometry(QtCore.QRect(40, 60, 55, 16))
        self.label_field.setText("")
        self.label_field.setObjectName("label_field")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(660, 10, 321, 441))
        self.groupBox_3.setObjectName("groupBox_3")
        self.pushButton_open = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_open.setGeometry(QtCore.QRect(10, 30, 93, 28))
        self.pushButton_open.setObjectName("pushButton_open")
        self.checkBox_plot_x_in_norm_freq = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_plot_x_in_norm_freq.setGeometry(QtCore.QRect(10, 60, 81, 20))
        self.checkBox_plot_x_in_norm_freq.setObjectName("checkBox_plot_x_in_norm_freq")
        self.radioButton_plot_CL = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_plot_CL.setEnabled(True)
        self.radioButton_plot_CL.setGeometry(QtCore.QRect(10, 80, 95, 20))
        self.radioButton_plot_CL.setChecked(True)
        self.radioButton_plot_CL.setObjectName("radioButton_plot_CL")
        self.radioButton_plot_neff = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_plot_neff.setGeometry(QtCore.QRect(10, 100, 95, 20))
        self.radioButton_plot_neff.setChecked(False)
        self.radioButton_plot_neff.setObjectName("radioButton_plot_neff")
        self.radioButton_plot_F = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_plot_F.setGeometry(QtCore.QRect(10, 120, 95, 20))
        self.radioButton_plot_F.setObjectName("radioButton_plot_F")
        self.lineEdit_thickness_value = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_thickness_value.setGeometry(QtCore.QRect(200, 60, 61, 22))
        self.lineEdit_thickness_value.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_thickness_value.setObjectName("lineEdit_thickness_value")
        self.label_thickness_header = QtWidgets.QLabel(self.groupBox_3)
        self.label_thickness_header.setGeometry(QtCore.QRect(110, 60, 91, 21))
        self.label_thickness_header.setObjectName("label_thickness_header")
        self.checkBox_hide_not_recognized = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_hide_not_recognized.setGeometry(QtCore.QRect(110, 90, 111, 20))
        self.checkBox_hide_not_recognized.setChecked(True)
        self.checkBox_hide_not_recognized.setObjectName("checkBox_hide_not_recognized")
        self.pushButton_open_folder = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_open_folder.setGeometry(QtCore.QRect(10, 160, 131, 28))
        self.pushButton_open_folder.setObjectName("pushButton_open_folder")
        self.checkBox_legend = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_legend.setGeometry(QtCore.QRect(110, 120, 111, 20))
        self.checkBox_legend.setChecked(True)
        self.checkBox_legend.setObjectName("checkBox_legend")
        self.listView = QtWidgets.QListView(self.groupBox_3)
        self.listView.setGeometry(QtCore.QRect(10, 200, 391, 192))
        self.listView.setObjectName("listView")
        self.pushButton_replot_list = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_replot_list.setGeometry(QtCore.QRect(160, 160, 61, 28))
        self.pushButton_replot_list.setObjectName("pushButton_replot_list")
        ModeViever.setCentralWidget(self.centralwidget)

        self.retranslateUi(ModeViever)
        QtCore.QMetaObject.connectSlotsByName(ModeViever)

    def retranslateUi(self, ModeViever):
        _translate = QtCore.QCoreApplication.translate
        ModeViever.setWindowTitle(_translate("ModeViever", "Mode Viewer 2.0"))
        self.groupBox.setTitle(_translate("ModeViever", "Curve"))
        self.groupBox_2.setTitle(_translate("ModeViever", "Field"))
        self.groupBox_3.setTitle(_translate("ModeViever", "Controls"))
        self.pushButton_open.setText(_translate("ModeViever", "Open txt file"))
        self.checkBox_plot_x_in_norm_freq.setText(_translate("ModeViever", "Norm freq"))
        self.radioButton_plot_CL.setText(_translate("ModeViever", "CL"))
        self.radioButton_plot_neff.setText(_translate("ModeViever", "neff"))
        self.radioButton_plot_F.setText(_translate("ModeViever", "F opt overl"))
        self.lineEdit_thickness_value.setText(_translate("ModeViever", "1.0"))
        self.label_thickness_header.setText(_translate("ModeViever", "Thickness [um]"))
        self.checkBox_hide_not_recognized.setText(_translate("ModeViever", "hide not recog"))
        self.pushButton_open_folder.setText(_translate("ModeViever", "Open folder with txt"))
        self.checkBox_legend.setText(_translate("ModeViever", "legend"))
        self.pushButton_replot_list.setText(_translate("ModeViever", "replot"))
