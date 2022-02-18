# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QMenu, QAction

from Utilities.Utilities import set_font_size


class TagButton(QWidget):

    def __init__(self, tag, in_controller, parent=None, ):
        QWidget.__init__(self, parent)

        self.tag = tag
        self.Controller = in_controller

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.button = QPushButton(tag)
        self.button.setFixedWidth(len(tag) * 11)
        self.button.setToolTip(tag)
        self.button.clicked.connect(self.serch_asset)

        self.button.setStyleSheet("QPushButton  { \n"
                                  "border-radius: 11px;\n"
                                  "background-color: #343b47;\n"
                                  "height: 23px;\n"
                                  "width: 86px;\n"
                                  "font: bold;"
                                  "color:rgb(200, 200, 200);}\n"

                                  "QPushButton:hover {\n"
                                  "color:#9bc2ff;"
                                  "background-color: #2c313c;"
                                  "}\n")

        # set font size
        size = self.Controller.ui.font_spinBox.value()
        set_font_size(self.button, size)

        self.layout.addWidget(self.button)

        # connect Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_handler)

    def serch_asset(self):
        self.Controller.ui.search_lineEdit.setText(self.tag)
        self.Controller.refresh_ui()

    def right_click_handler(self, pos):
        menu = QMenu()
        menu.setStyleSheet("""background-color: #16191d; color: #fff;""")
        menu.addAction(QAction("Add teg to search line", self))
        action = menu.exec_(QCursor().pos())
        if action:
            if action.text() == "Add teg to search line":
                tags = self.Controller.ui.search_lineEdit.text() + " " + self.tag
                self.Controller.ui.search_lineEdit.setText(tags)
                self.Controller.refresh_ui()
            else:
                pass
