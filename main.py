import os
import sys
from urllib import request
from PyQt5 import QtWidgets
from PyQt5.uic import loadUiType

from my_vk import vk_class

main_win, _ = loadUiType(os.path.join('res', 'design', 'main.ui'))
properties_win, _ = loadUiType(os.path.join('res', 'design', 'properties.ui'))


class MainWindow(QtWidgets.QMainWindow, main_win):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.properties.clicked.connect(lambda: w.setCurrentIndex(1))
        self.commit.clicked.connect(lambda: w.setCurrentIndex(1))


class Properties(QtWidgets.QMainWindow, properties_win):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.cancle.clicked.connect(lambda: w.setCurrentIndex(0))


if __name__ == "__main__":
    vk = vk_class()
    app = QtWidgets.QApplication(sys.argv)
    # Append windows
    main_window = MainWindow()
    properties_window = Properties()
    # Set window
    w = QtWidgets.QStackedWidget()
    w.addWidget(main_window)
    w.addWidget(properties_window)
    w.resize(800, 600)
    w.show()
    sys.exit(app.exec_())
