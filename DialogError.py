# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DialogError.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

part2 = "<span style=\" font-size:10pt;\">Извините, это расширение файла не поддерживается"
part = "<html><head/><body><p>"
part3 = "</span></p></body></html>"


class Ui_DialogError(object):
    def setupUi(self, DialogError):
        DialogError.setObjectName("DialogError")
        DialogError.resize(340, 87)
        DialogError.setFocusPolicy(QtCore.Qt.NoFocus)
        self.error_text = QtWidgets.QLabel(DialogError)
        self.error_text.setGeometry(QtCore.QRect(10, 20, 331, 51))
        self.error_text.setObjectName("error_text")

        self.retranslateUi(DialogError)
        QtCore.QMetaObject.connectSlotsByName(DialogError)

    def retranslateUi(self, DialogError):
        _translate = QtCore.QCoreApplication.translate
        DialogError.setWindowTitle(_translate("DialogError", "Ошибка"))
        self.error_text.setText(_translate("DialogError", part2 + part + part3))
