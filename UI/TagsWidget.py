# -*- coding: utf-8 -*-
from random import randint

from PyQt5.QtCore import Qt, QVariantAnimation, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QFrame, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QScrollArea


class TagsWidget(QWidget):
    def __init__(self, parent=None, spacing=12):
        QWidget.__init__(self, parent)

        self.spacing = spacing
        self.tag_vidget_list = []

        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.__layout)

        self.left_button = QPushButton("")
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/icons/chevrons-left.svg"), QIcon.Normal, QIcon.Off)
        self.left_button.setIcon(icon)
        self.left_button.setIconSize(QSize(24, 24))
        self.__layout.addWidget(self.left_button)
        self.left_button.setFixedWidth(30)

        self.__background = QFrame()
        self.__background_layout = QHBoxLayout(self.__background)
        self.__background_layout.setContentsMargins(0, 0, 0, 0)
        self.__background_layout.setSpacing(self.spacing)

        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setWidget(self.__background)
        self.__scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__layout.addWidget(self.__scroll_area)

        self.right_button = QPushButton("")
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/icons/chevrons-right.svg"), QIcon.Normal, QIcon.Off)
        self.right_button.setIcon(icon)
        self.right_button.setIconSize(QSize(24, 24))
        self.__layout.addWidget(self.right_button)
        self.right_button.setFixedWidth(30)

        self.left_button.clicked.connect(lambda: self.move_widgets("left"))
        self.right_button.clicked.connect(lambda: self.move_widgets("right"))

    def clear(self):
        if self.__background_layout.count():
            for i in range(self.__background_layout.count()):
                self.__background_layout.itemAt(i).widget().deleteLater()
        self.tag_vidget_list = []

    def add_widget(self, widget):
        self.__background_layout.addWidget(widget)
        self.tag_vidget_list.append(widget)

    def add_widgets(self, widget_list):
        for widget in widget_list:
            self.__background_layout.addWidget(widget)
        self.tag_vidget_list = widget_list

    def move_widgets(self, dirrect):
        scroll_bar = self.__scroll_area.horizontalScrollBar()
        if dirrect == "right":
            ofset = scroll_bar.value() + scroll_bar.pageStep()
        else:
            ofset = scroll_bar.value() - scroll_bar.pageStep()

        self.ani = QVariantAnimation()
        self.ani.setStartValue(scroll_bar.value())
        self.ani.setEndValue(ofset)
        self.ani.setDuration(300)
        self.ani.valueChanged.connect(self.update_scroll_position)
        self.ani.start()

    def update_scroll_position(self, value):
        self.__scroll_area.horizontalScrollBar().setValue(int(value * 1))


if __name__ == "__main__":
    import sys


    class MyWindow(QWidget):
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            self.vbox = QVBoxLayout()
            # self.tag_widget = TagsWidget()
            # self.vbox.addWidget(self.tag_widget)

            # b1 = QPushButton("b1")
            # self.tag_widget.add_widget(b1)
            # b1.clicked.connect(lambda: self.print_tx("i"))
            #
            # b2 = QPushButton("b2")
            # self.tag_widget.add_widget(b2)
            # b2.clicked.connect(lambda: self.print_tx("ggg"))

            tx = ["t0", "t1", "t2", "t3", "t4"]
            ff = list(range(5))

            for i in range(len(tx)):
                print(i)
                gg = tx[:]

                def print_t():
                    print(gg[i])

                but = QPushButton(gg[i])
                self.vbox.addWidget(but)
                but.clicked.connect(print_t)

            self.setLayout(self.vbox)


    app = QApplication(sys.argv)
    window = MyWindow()
    # window.resize(500, 300)
    window.show()
    sys.exit(app.exec_())
