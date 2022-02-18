import re
from PyQt5.QtWidgets import QMainWindow
from Asset import Asset
from UI.MainWindow import MainWindow
from Utilities.Logging import logger
from Utilities.Utilities import get_library_path


class Controller(QMainWindow):
    """
    Class represents a controller implementation.
    Connect the ui with the model
    """
    def __init__(self, in_model, application, parent=None):
        super(QMainWindow, self).__init__(parent)

        # tags received from the interface
        self.current_tags = []

        # tags and assets received from the database based on the current tags
        self.found_tags = []
        self.found_assets = []

        # The constructor get model references.
        self.Models = in_model

        self.application = application

        # get path to asset library
        self.lib_path = get_library_path()
        self.connect_db = self.Models.initialize(self.lib_path)

        # create Ui
        self.ui = MainWindow(self)

        # list of observers reacting to changes in current tags
        self._observers = [self, self.ui]

        # if we have old data we use it
        if self.ui.search_lineEdit.text() and self.connect_db:
            self.refresh_ui()

    def create_asset(self):
        """
        get asset data from ui
        """
        logger.debug("\n\n__________________Create asset clicked___________________")
        asset_data = self.ui.get_asset_data()
        # create asset
        if asset_data:
            Asset(self, **asset_data).create()
            self.ui.clear_form()
            logger.debug(" executed")

    def edit_asset(self):
        """
        get asset data from ui
        """
        logger.debug("\n\n__________________Edit asset clicked___________________")
        asset_data = self.ui.get_asset_data()
        # edit asset
        if asset_data:
            Asset(self, **asset_data).edit_asset()
            self.ui.clear_form()
            logger.debug(" executed")

    def refresh_ui(self):
        """
        Getting tags from linEdit and refresh_ui
        """
        self.current_tags = re.findall(r'[0-9A-z_]+', self.ui.search_lineEdit.text())
        if self.connect_db:
            self.notify_observers()
            logger.debug(" executed")
        else:
            logger.error("Database path required for initialization\n")

    def current_state_changed(self):
        """
        When entering new tags, we find the corresponding tags and assets
        """
        if self.current_tags:
            logger.debug(f"Started searching by tags {' '.join(self.current_tags)}")
            self.found_assets = self.Models.find_assets_by_tag_list(self.current_tags)
            if self.found_assets:
                self.found_tags = self.Models.find_tags_by_asset_list(self.found_assets)

    def get_from_folder(self, path):
        logger.debug("\n\n__________________Find asset in folder clicked___________________")
        logger.debug(path)
        self.found_assets = self.Models.get_all_from_folder(path)
        if self.found_assets:
            self.found_tags = self.Models.find_tags_by_asset_list(self.found_assets)
        self.ui.current_state_changed()

    def notify_observers(self):
        for x in self._observers:
            x.current_state_changed()


if __name__ == '__main__':
    pass

    # template:

    # import sys
    # class SimpleWindow(QWidget):
    #     def __init__(self):
    #         super(SimpleWindow, self).__init__()
    #         ly = QHBoxLayout(ly)
    #         self.setLayout()
    #
    #         self.resize(500, 400)
    #
    #
    # app = QApplication(sys.argv)
    # window = SimpleWindow()
    # window.show()
    #
    # app.exec_()
