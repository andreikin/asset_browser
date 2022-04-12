# -*- coding: utf-8 -*-
from random import randint
from itertools import cycle

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFrame, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget, \
    QScrollArea


class GalleryWidget(QWidget):
    """
    widget displaying child widgets as a pinterest gallery
    """
    scroll_bar_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None, icons_width=50, spacing=5):
        QWidget.__init__(self, parent)

        self.widget_list = []
        self.icons_width = icons_width
        self.spacing = spacing
        self.setMinimumWidth(self.icons_width+30)

        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(self.spacing)
        self.__layout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.__layout)

        self.__background = QFrame()
        self.__background.setContentsMargins(0, 0, 0, 0)
        self.__background_layout = QHBoxLayout(self.__background)
        self.__background_layout.setSpacing(self.spacing)
        self.__background_layout.setAlignment(QtCore.Qt.AlignTop)

        self.__columns_layout_list = []
        for i in range(int(4000 / icons_width)):
            v_layout = QVBoxLayout()
            v_layout.setAlignment(QtCore.Qt.AlignTop)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.setSpacing(self.spacing)
            self.__background_layout.addLayout(v_layout)
            self.__columns_layout_list.append(v_layout)

        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setWidget(self.__background)
        self.__layout.addWidget(self.__scroll_area)
        self.__scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.scroll_bar = self.__scroll_area.verticalScrollBar()
        self.scroll_bar.valueChanged.connect(self.scroll_bar_handler)

    def scroll_bar_handler(self):
        """
        Starts the asset loading function
        """
        try:
            if (self.scroll_bar.maximum() - 150) < self.scroll_bar.value():
                self.scroll_bar_signal.emit()
        except Exception as message:
            print(message)

    def add_widget(self, widget):
        self.widget_list.append(widget)
        self.refresh()

    def clear(self):
        for layout in self.__columns_layout_list:
            if layout.count():
                for i in range(layout.count()):
                    layout.itemAt(i).widget().deleteLater()
        self.widget_list = []

    def refresh(self, event=None):
        """
        reposition assets on window resize
        """
        win_width = self.width() if not event else event.size().width()
        columns_num = win_width / (self.icons_width + self.spacing)
        if not columns_num:
            columns_num = 1
        tmp_image_list = self.widget_list[::-1]
        cycler = cycle(range(int(columns_num)))
        while tmp_image_list:
            current_image = tmp_image_list.pop()
            self.__columns_layout_list[next(cycler)].addWidget(current_image)

    def resizeEvent(self, event):
        if self.widget_list:
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
