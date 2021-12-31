# -*- coding: utf-8 -*-
from random import randint
from itertools import cycle
from time import sleep

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget, \
    QScrollArea


class TagsWidget(QWidget):
    def __init__(self, parent=None, spacing=5):
        QWidget.__init__(self, parent)


        self.spacing = spacing
        self.vidget_list = []

        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.__layout)

        self.left_button = QPushButton("<<")
        self.__layout.addWidget(self.left_button)

        self.__background = QFrame()
        self.__background_layout = QHBoxLayout(self.__background)
        #self.__background_layout.setAlignment(Qt.AlignTop)

        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setWidget(self.__background)
        self.__scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__layout.addWidget(self.__scroll_area)

        self.right_button = QPushButton(">>")
        self.__layout.addWidget(self.right_button)

        self.left_button.clicked.connect(lambda :  self.move_widgets("left"))
        self.right_button.clicked.connect(lambda: self.move_widgets("right"))

        style_sheet = """
                               QScrollArea {
                                   border-top: 3px transparent; }
                               """
        self.setStyleSheet(style_sheet)

    def add_widget(self, widget):
        self.__background_layout.addWidget(widget)

    def move_widgets(self, dirrect):
        scroll_bar = self.__scroll_area.horizontalScrollBar()
        frames = 10
        for _ in range(frames):
            if dirrect == "right":
                ofset = scroll_bar.value() + int(scroll_bar.pageStep()/frames)
            else:
                ofset = scroll_bar.value() - int(scroll_bar.pageStep()/frames)
            sleep(0.02)
            scroll_bar.setValue(ofset)







if __name__ == "__main__":
    import sys


    class MyWindow(QWidget):
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            self.vbox = QVBoxLayout()
            self.tag_widget = TagsWidget( )
            self.vbox.addWidget(self.tag_widget)
           
            for x in range(25):
                but = QPushButton(str(x))
                self.tag_widget.add_widget(but)
                but.setFixedSize(70, 20)

            self.setLayout(self.vbox)


    app = QApplication(sys.argv)
    window = MyWindow()
    #window.resize(500, 300)
    window.show()
    sys.exit(app.exec_())
