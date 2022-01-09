# -*- coding: utf-8 -*-
from random import randint

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout


class TagWidget(QWidget):
    def __init__(self, tag, inController, parent=None, ):
        QWidget.__init__(self, parent)
        self.tag = tag
        self.Controller = inController

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.button = QPushButton(tag)
        self.button.setFixedWidth(len(tag)*11)
        self.button.setToolTip(tag)
        self.button.clicked.connect(self.serch_asset)

        self.button.setStyleSheet("QPushButton  { \n"
                                  "border-radius: 11px;\n"
                                  "background-color: #343b47;\n"
                                  "height: 23px;\n"
                                  "width: 86px;\n"
                                  "color:rgb(200, 200, 200);}\n"

                                  "QPushButton:hover {\n"
                                  "background-color: #2c313c;}\n"

                                  "QPushButton:pressed {\n"
                                  "background-color: rgb(36, 36, 36); }\n")

        self.layout.addWidget(self.button)

    def serch_asset(self):
        self.Controller.ui.search_lineEdit.setText(self.tag)
        self.Controller.get_current_tags()
