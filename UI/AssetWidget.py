# -*- coding: utf-8 -*-
from random import randint

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFrame, QSizePolicy



class AssetWidget(QWidget):
    def __init__(self, asset, inModels, parent=None, width=150, height=200):
        QWidget.__init__(self, parent)
        self.asset = asset
        self.Models = inModels
        self.height = height
        self.width = width

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.base_frame = QFrame()
        self.base_frame.setFixedSize(width, height)
        self.layout.addWidget(self.base_frame)

        self.button_layout = QVBoxLayout(self.base_frame)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(0)

        self.up_button = QPushButton(str(self.asset.id)+"_"+str(self.asset.name))
        self.button_layout.addWidget(self.up_button)
        self.up_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.up_button.setStyleSheet("QPushButton  { \n"
                                     "font: 12pt 'Tahoma';\n"
                                     "border-top-left-radius: 8px;\n"
                                     "border-top-right-radius: 8px;\n"
                                     "background-color: #343b47;\n"
                                     "color:rgb(90, 90, 90);}\n"
                                     "QPushButton:hover {\n"
                                     "color:rgb(118, 118, 118);\n"
                                     "background-color: #2c313c;}\n"
                                     "QPushButton:pressed {\n"
                                     "background-color: rgb(36, 36, 36); }\n")

        self.dw_button = QPushButton("Delite asset")

        self.dw_button.clicked.connect(lambda: self.Models.delete_asset(asset.id))

        self.button_layout.addWidget(self.dw_button)
        self.dw_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.dw_button.setFixedHeight(30)
        self.dw_button.setStyleSheet("QPushButton  { \n"
                                     "border-bottom-left-radius: 8px;\n"
                                     "border-bottom-right-radius: 8px;\n"
                                     "background-color: #2c313c;\n"
                                     "color:rgb(90, 90, 90);}\n"
                                     "QPushButton:hover {\n"
                                     "color:rgb(118, 118, 118);\n"
                                     "background-color: rgb(40,40, 40);}\n"
                                     "QPushButton:pressed {\n"
                                     "background-color: rgb(0, 0, 0); }\n")

    #def delite_widget(self):






