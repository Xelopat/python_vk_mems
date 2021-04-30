import json
import os
import sys
import threading
from shutil import rmtree
from time import sleep
from urllib.request import urlretrieve

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUiType

from my_vk import vk_class

main_win, _ = loadUiType(os.path.join('res', 'design', 'main.ui'))
properties_win, _ = loadUiType(os.path.join('res', 'design', 'properties.ui'))
post_win, _ = loadUiType(os.path.join('res', 'design', 'post.ui'))


class MainWindow(QtWidgets.QMainWindow, main_win):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.auth.clicked.connect(lambda: vk.auth())
        self.append.clicked.connect(lambda: self.append_group())
        self.remove.clicked.connect(lambda: self.remove_group())
        self.reload.clicked.connect(lambda: self.reload_group())

        self.dialog = uic.loadUi("res/design/dialog.ui")
        self.dialog.ok.clicked.connect(lambda: self.close_dialog())

    def append_group(self):
        count = vk.append_group(self.input_append.toPlainText())
        self.input_append.setText("")
        self.open_dialog("Всего групп: " + str(count))

    def remove_group(self):
        count = vk.remove_group(self.input_remove.toPlainText())
        self.input_remove.setText("")
        self.open_dialog("Всего групп: " + str(count))

    def reload_group(self):
        count = vk.reload()
        self.open_dialog("Обновлено групп: " + str(count))

    def open_dialog(self, text):
        self.dialog.label.setText(text)
        self.dialog.show()

    def close_dialog(self):
        self.dialog.close()


class Properties(QtWidgets.QMainWindow, properties_win):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

    def change_prop(self):
        try:
            with open("res/properties.json", "r") as read_file_prop:
                prop_data = json.load(read_file_prop)
        except FileNotFoundError:
            pass
        login = self.input_login.toPlainText()
        password = self.input_password.toPlainText()
        group_id = self.input_group.toPlainText()
        multiplier = self.input_multiplier.toPlainText()
        if login == "":
            login = prop_data["login"]
        if password == "":
            password = prop_data["password"]
        if group_id == "":
            group_id = prop_data["group_id"]
        if multiplier == "":
            multiplier = prop_data["multiplier"]
        prop_data = {"login": login, "password": password, "multiplier": float(multiplier), "group": group_id}
        with open("res/properties.json", "w") as write_file_prop:
            json.dump(prop_data, write_file_prop)
        w.setCurrentIndex(0)


class Post(QtWidgets.QMainWindow, post_win):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.count_posts = 0
        self.work = False
        self.setupUi(self)
        self.all_posts = []
        self.now_img = 0
        self.pixmap = []
        self.i_think = []
        self.img_right.clicked.connect(lambda: self.next_picture())
        self.img_left.clicked.connect(lambda: self.prev_picture())
        self.add.clicked.connect(lambda: self.append_post())
        self.skip.clicked.connect(lambda: self.skip_post())
        self.block.clicked.connect(lambda: self.remove_group())

    def worker(self):
        count = 0
        while self.work:
            if post_window.all_posts:
                vk.posting(post_window.all_posts[0])
                del post_window.all_posts[0]
                count += 1
                self.post_max.setText(f"{count}/50")
            if count == 50:
                self.work = False
            sleep(15)

    def start_posting(self):
        self.work = True
        thread = threading.Thread(target=self.worker)
        thread.start()
        self.all_posts = []
        self.now_img = 0
        self.pixmap = []
        self.i_think = []
        posting = ""
        i = 0
        while posting != "end":
            post_list, percent, posting = vk.post(i)
            if post_list != "end":
                self.progress.setValue(percent)
                for x in post_list:
                    self.i_think.append(x)
            i += 1
            if i == 1:
                self.show_post()

    def show_post(self):
        if not self.i_think:
            return
        try:
            os.mkdir("cache", 0o755)
        except OSError:
            pass
        self.now_img = 0
        post = self.i_think[0]
        message = post["text"]
        self.message.setText(message)
        info = "vk.com/" + post["link"] + " " + post["info"]
        self.info.setText(info)
        self.pixmap = []
        for i in range(len(post["img"])):
            urlretrieve(post["img"][i], f"cache/{i}.jpg")
            pixmap0 = QPixmap(f"cache/{i}.jpg")
            width = pixmap0.width()
            height = pixmap0.height()
            if height < width:
                self.pixmap.append(pixmap0.scaled(500, int(500 / width * height)))
            else:
                self.pixmap.append(pixmap0.scaled(int(500 / height * height), 500))
        self.img.setPixmap(self.pixmap[0])
        rmtree('cache')

    def append_post(self):
        message = self.message.toPlainText()
        attachment = self.i_think[0]["attachment"]
        owner_id = self.i_think[0]["owner_id"]
        self.all_posts.append([message, attachment, "https://vk.com/" + self.i_think[0]["link"]])
        del self.i_think[0]
        self.show_post()
        self.write_yet(self.i_think[0]["link"])

    def skip_post(self):
        del self.i_think[0]
        self.show_post()
        self.write_yet(self.i_think[0]["link"])

    def remove_group(self):
        vk.remove_group(str(self.i_think[0]["owner_id"]))
        del self.i_think[0]
        self.show_post()

    def next_picture(self):
        self.now_img += 1
        if self.now_img == len(self.pixmap):
            self.now_img = 0
        self.img.setPixmap(self.pixmap[self.now_img])

    def prev_picture(self):
        self.now_img -= 1
        if self.now_img < 0:
            self.now_img = len(self.pixmap) - 1
        self.img.setPixmap(self.pixmap[self.now_img])

    @staticmethod
    def write_yet(text):
        try:
            with open("res/yet.txt", "a") as write_file:
                write_file.write(text + " ")
        except FileNotFoundError:
            with open("res/yet.txt", "w") as write_file:
                write_file.write(text + " ")


vk = vk_class()
app = QtWidgets.QApplication(sys.argv)
# Append windows
main_window = MainWindow()
properties_window = Properties()
post_window = Post()
# Set window
w = QtWidgets.QStackedWidget()
w.addWidget(main_window)
w.addWidget(properties_window)
w.addWidget(post_window)

properties_window.cancle.clicked.connect(lambda: w.setCurrentIndex(0))
properties_window.commit.clicked.connect(lambda: properties_window.change_prop())

main_window.properties.clicked.connect(lambda: w.setCurrentIndex(1))
main_window.start.clicked.connect(lambda: start_post())

post_window.cancle.clicked.connect(lambda: end_post())


def start_post():
    w.setCurrentIndex(2)
    w.setGeometry(w.x(), w.y() - 25, 800, 750)
    post_window.start_posting()


def end_post():
    w.setCurrentIndex(0)
    w.setGeometry(w.x(), w.y() + 50, 800, 600)


w.resize(800, 600)
w.show()
sys.exit(app.exec_())
