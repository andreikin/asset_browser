import re
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from UI.MainWindow import MainWindow
from Models import Models


class Controller(QMainWindow):
    """
    Class represents a controller implementation.
    Connect the ui with the model
    """

    def __init__(self, in_models, parent=None):
        super(QMainWindow, self).__init__(parent)

        """ tags received from the interface"""
        self.current_tags = []

        """ tags and assets received from the database based on the current tags """
        self.found_tags = []
        self.found_assets = []

        """ The constructor get model references. """
        self.Models = in_models

        """ create Ui """
        self.ui = MainWindow(self)

        """ list of observers reacting to changes in current tags """
        self._observers = [self, self.ui]

        """ connect Ui to functions"""
        self.ui.add_asset_button.clicked.connect(self.create_asset)
        self.ui.search_button.clicked.connect(self.get_current_tags)
        self.ui.search_lineEdit.returnPressed.connect(self.get_current_tags)

        """ if we have old data we use it """
        if self.ui.search_lineEdit.text():
            self.get_current_tags()

    def create_asset(self):
        asset_data = self.ui.get_asset_data()
        self.Models.add_asset(**asset_data)
        # TODO: Add ui filling verification

    def get_current_tags(self):
        """
        Getting tags from linEdit
        """
        self.current_tags = re.findall(r'[0-9A-z_]+', self.ui.search_lineEdit.text())
        self.notify_observers()

    def current_state_changed(self):
        """
        When entering new tags, we find the corresponding tags and assets
        """
        self.found_assets = self.Models.find_assets_by_tag_list(self.current_tags)
        if self.found_assets:
            self.found_tags = self.Models.find_tags_by_asset_list(self.found_assets)


    def notify_observers(self):
        for x in self._observers:
            x.current_state_changed()


if __name__ == '__main__':
    pass
    app = QApplication(sys.argv)
    window = Controller(Models)
    window.show()

    app.exec_()
