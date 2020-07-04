# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\pantalla.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from src.main_thread import MainThread

import time
import string  
import json 
import datetime


class Ui_MainWindow(object):
    def __init__(self):
        self.i = 0

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton_ui_config = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_ui_config.setGeometry(QtCore.QRect(660, 460, 93, 21))
        self.pushButton_ui_config.setObjectName("pushButton_ui_config")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(270, 20, 221, 81))
        font = QtGui.QFont()
        font.setPointSize(27)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(50, 250, 191, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.lcdNumber_ui_temp = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber_ui_temp.setGeometry(QtCore.QRect(240, 250, 131, 41))
        self.lcdNumber_ui_temp.setObjectName("lcdNumber_ui_temp")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.main_thread = MainThread()
        self.main_thread.start()


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_ui_config.setText(_translate("MainWindow", "Configuracion"))
        self.label.setText(_translate("MainWindow", "AUTEMDE"))
        self.label_3.setText(_translate("MainWindow", "Temperatura actual:"))

        #User Code
        self.pushButton_ui_config.clicked.connect(self.on_button_clicked)

    def on_button_clicked(self):
        print("Clicked")
        self.i += 1
        self.lcdNumber_ui_temp.display(32 + float(self.i) / 10)


if __name__ == "__main__":
    self.main_thread = MainThread()
    self.tcp_client = TcpClient()
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())


'''
def publish_msg():
    x = {
        "name": id_fields[5] + " " + id_fields[6],
        "lastName" : id_fields[3] + " " + id_fields[4],
        "id" : id_fields[2],
        "birthday" : id_fields[8],
        "temperature": temperature,
        "company" : "62b15004-a85d-11ea-bb37-0242ac130002",
        "device" : "dbafb884-a85c-11ea-bb37-0242ac130002",
        "timestamp" : int(datetime.datetime.now().timestamp()) * 1000
    }

    print(json.dumps(x))
    mqtt_client.publish_msg(json.dumps(x))

mqtt_client = MQTTClient()
id_scanner = IDScanner(id_card_detected)
pyrometer = Pyrometer(temperature_taken)

is_card_detected = False
is_temperature_taken = False
id_fields = list()
temperature = ""

if __name__ == "__main__":

    id_scanner.start()
    while True:
        if is_card_detected and not is_temperature_taken:
            pyrometer.measure()
        elif is_card_detected and is_temperature_taken:
            publish_msg()
            is_card_detected = False
            is_temperature_taken = False
        time.sleep(1.5)

    print("Main thread finished!")




'''