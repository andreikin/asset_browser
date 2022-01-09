# -*- coding: utf-8 -*-
from random import randint

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFrame, QSizePolicy, QApplication

from Models import Models


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


        self.up_button = QPushButton("")
        self.button_layout.addWidget(self.up_button)
        self.up_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.up_button.setStyleSheet("QPushButton  { \n"
                                     "border-radius: 12px;\n"
                                     "border-image: url("+asset.image+") 3 10 3 10;\n"
                                     "background-color: #343b47;\n"
                                     "color:rgb(90, 90, 90);}\n" )


if __name__ == "__main__":
    import sys

    class MyWindow(QWidget):
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            self.vbox = QVBoxLayout()
            asset = Models.find_assets_by_tag_list(["Help",])[0]
            # print(asset.image)
            # asset.image = "D:/03_andrey/py_progects/asset_browser/images/im_12.PNG"
            # asset.save()
            # print(asset.image)

            self.gallery = AssetWidget(asset, Models)
            self.vbox.addWidget(self.gallery)

            self.setLayout(self.vbox)



    app = QApplication(sys.argv)
    window = MyWindow()
    window.resize(500, 300)
    window.show()
    sys.exit(app.exec_())





