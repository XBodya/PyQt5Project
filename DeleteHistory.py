# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'delhist.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DeleteHistory(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(541, 194)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(19, 9, 511, 141))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_delete_last_fives = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton_delete_last_fives.setObjectName("pushButton_delete_last_fives")
        self.gridLayout.addWidget(self.pushButton_delete_last_fives, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_delete_interval = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton_delete_interval.setObjectName("pushButton_delete_interval")
        self.horizontalLayout.addWidget(self.pushButton_delete_interval)
        self.lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)
        self.pushButton_delete_last = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton_delete_last.setInputMethodHints(QtCore.Qt.ImhNone)
        self.pushButton_delete_last.setObjectName("pushButton_delete_last")
        self.gridLayout.addWidget(self.pushButton_delete_last, 0, 0, 1, 1)
        self.pushButton_delete_all = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton_delete_all.setObjectName("pushButton_delete_all")
        self.gridLayout.addWidget(self.pushButton_delete_all, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 541, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Очистить историю"))
        self.pushButton_delete_last_fives.setText(_translate("MainWindow", "Удалить последние 5 файлов"))
        self.pushButton_delete_interval.setText(_translate("MainWindow", "Удалить интервал"))
        self.pushButton_delete_last.setText(_translate("MainWindow", "Удалить последний файл"))
        self.pushButton_delete_all.setText(_translate("MainWindow", "Удалить всё"))