import sys
from random import randint

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton

from UI.AssetWidget import AssetWidget
from UI.GalleryWidget import GalleryWidget
from UI.Ui_MainWindow import Ui_MainWindow


COLUMN_WIDTH = 110
SPACING = 10
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, inController, parent=None):
        super(QMainWindow, self).__init__(parent)

        self.Controller = inController

        self.setupUi(self)

        self.gallery = GalleryWidget(icons_width=COLUMN_WIDTH, spacing=SPACING)
        self.galery_VLayout.addWidget(self.gallery)
        self.add_assets_widgets()

    def add_assets_widgets(self):
        self.gallery.clear()
        for asset in self.Controller.found_assets:
            asset_widget = AssetWidget(asset, self.Controller.Models, width=COLUMN_WIDTH, height=randint(120, 200))
            print(asset.name)
            self.gallery.add_widget(asset_widget)

    def current_state_changed(self):
        self.add_assets_widgets()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    for x in range(135):
        but = QPushButton()
        but.setFixedHeight(randint(50, 150))
        window.gallery.add_widget(but)

    window.show()
    app.exec_()
