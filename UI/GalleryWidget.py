# -*- coding: utf-8 -*-
from random import randint
from itertools import cycle
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget, \
    QScrollArea


class GalleryWidget(QWidget):
    def __init__(self, parent=None, icons_width=50, spacing=5):
        QWidget.__init__(self, parent)
        
        self.icons_width = icons_width
        self.spacing = spacing
        self.vidget_list = []

        self.setAcceptDrops(True)

        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(self.spacing)
        self.__layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.__layout)

        self.__background = QFrame()
        self.__background.setContentsMargins(0, 0, 0, 0)
        self.__background_layout = QHBoxLayout(self.__background)
        self.__background_layout.setSpacing(self.spacing)
        self.__background_layout.setAlignment(Qt.AlignTop)

        self.__columns_layout_list = []
        for i in range(int(4000 / icons_width)):
            v_layout = QVBoxLayout()
            v_layout.setAlignment(Qt.AlignTop)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.setSpacing(self.spacing)
            self.__background_layout.addLayout(v_layout)
            self.__columns_layout_list.append(v_layout)

        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setWidget(self.__background)
        self.__layout.addWidget(self.__scroll_area)
        self.__scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def add_widget(self, widget):
        self.vidget_list.append(widget)
        self.refresh()

    def clear(self):
        for layout in self.__columns_layout_list:
            if layout.count():
                for i in range(layout.count()):
                    layout.itemAt(i).widget().deleteLater()
        self.vidget_list = []

    def refresh(self, event=None):
        win_width = self.width() if not event else event.size().width()
        columns_num = win_width / (self.icons_width + self.spacing)
        if not columns_num:
            columns_num = 1
        tmp_image_list = self.vidget_list[::-1]
        cycler = cycle(range(int(columns_num)))
        while tmp_image_list:
            current_image = tmp_image_list.pop()
            self.__columns_layout_list[next(cycler)].addWidget(current_image)

    def resizeEvent(self, event):
        if self.vidget_list:
            self.refresh(event)




if __name__ == "__main__":
    import sys


    class MyWindow(QWidget):
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            self.vbox = QVBoxLayout()
            self.gallery = GalleryWidget(icons_width=100, spacing=8)
            self.vbox.addWidget(self.gallery)
            for x in range(135):
                but = QPushButton()
                but.setFixedHeight(randint(50, 150))
                self.gallery.add_widget(but)
            style_sheet = """
                       QPushButton {
                           border-radius: 4px;
                           background-color: rgb(200, 200, 200); }
                       """
            self.setStyleSheet(style_sheet)



            self.setLayout(self.vbox)



    app = QApplication(sys.argv)
    window = MyWindow()
    window.resize(500, 300)
    window.show()
    sys.exit(app.exec_())
