import sys
from urllib import request

from PyQt5 import QtWidgets, uic


class my_window(QtWidgets.QMainWindow):
    def __init__(self):
        super(my_window, self).__init__()
        self.ui = Properties()
        self.ui.setupUi(self)

    def main(self):
        self.ui = Main()
        self.ui.setupUi(self)

    def load_img(self, link):
        resource = request.urlopen(link)
        out = open("img.jpg", 'wb')
        out.write(resource.read())
        out.close()


app = QtWidgets.QApplication([])
application = my_window()
application.show()

sys.exit(app.exec())
