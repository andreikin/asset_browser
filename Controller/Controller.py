import re
import sys
from random import randint

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from UI.MainWindow import MainWindow
from UI.AssetCreationDialog import AssetCreationDialog
from Models import Models


class Controller(QMainWindow):
    """
    Class represents a controller implementation.
    Connect the ui with the model
    """

    def __init__(self, in_models, parent=None):
        super(QMainWindow, self).__init__(parent)

        self.current_tags = []
        self.found_tags = []
        self.found_assets = []

        """ The constructor get model references. """
        self.Models = in_models

        """ create Ui """
        self.ui = MainWindow(self)

        """ list of observers reacting to changes in current tags """
        self._observers = [self, self.ui]

        """ connect Ui to functions"""
        self.ui.create_asset_button.clicked.connect(self.create_asset_dialog)
        self.ui.search_button.clicked.connect(self.get_tags)
        self.ui.clear_button.clicked.connect(self.ui.gallery.clear)

    def create_asset_dialog(self):
        asset_data = AssetCreationDialog()
        if asset_data.exec_():
            asset_data = asset_data.get_asset_data()
            self.Models.add_asset(**asset_data)
        return asset_data

    def get_tags(self, tag=None):
        if not tag:
            self.current_tags = re.findall(r'[0-9A-z_]+', self.ui.search_lineEdit.text())
        else:
            self.current_tags = [tag]
        self.notify_observers()

    def search_asset(self):
        self.found_assets = self.Models.find_asset_by_tag_list(self.current_tags)

    def current_state_changed(self):
        self.search_asset()

    def notify_observers(self):
        for x in self._observers:
            x.current_state_changed()


if __name__ == '__main__':
    pass
    app = QApplication(sys.argv)
    window = Controller(Models)
    window.show()

    app.exec_()
