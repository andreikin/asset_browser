import json
import os
import re
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout

from Asset import Asset
from UI.MainWindow import MainWindow
from Utilities.Logging import logger
from Utilities.Utilities import get_db_path


class Controller(QMainWindow):
    """
    Class represents a controller implementation.
    Connect the ui with the model
    """

    def __init__(self, in_model, parent=None):
        super(QMainWindow, self).__init__(parent)

        # tags received from the interface
        self.current_tags = []

        # tags and assets received from the database based on the current tags
        self.found_tags = []
        self.found_assets = []

        # The constructor get model references.
        self.Models = in_model

        # get path and initialize data base
        self.db_path = get_db_path()
        self.Models.initialize(self.db_path)
        logger.debug("Database " + self.db_path + "  initialized successfully!")

        # get path to asset library
        self.lib_path = os.path.dirname(self.db_path)

        # create Ui
        self.ui = MainWindow(self)

        # list of observers reacting to changes in current tags
        self._observers = [self, self.ui]

        # if we have old data we use it
        if self.ui.search_lineEdit.text():
            self.refresh_ui()

        # temp function for filling ui
        #self.temp_asset_filling()

    def create_asset(self):
        # get asset data from ui
        asset_data = self.ui.get_asset_data()
        # create asset
        if asset_data:
            Asset(self, **asset_data).create()
            logger.debug(" executed")

    def edit_asset(self):
        # get asset data from ui
        asset_data = self.ui.get_asset_data()
        # edit asset
        if asset_data:
            Asset(self, **asset_data).edit_asset()
            logger.debug(" executed")

    def refresh_ui(self):
        """
        Getting tags from linEdit and refresh_ui
        """
        self.current_tags = re.findall(r'[0-9A-z_]+', self.ui.search_lineEdit.text())
        self.notify_observers()
        logger.debug(" executed\n")

    def current_state_changed(self):
        """
        When entering new tags, we find the corresponding tags and assets
        """
        logger.debug(f"Started searching by tags {' '.join(self.current_tags)}")
        self.found_assets = self.Models.find_assets_by_tag_list(self.current_tags)
        if self.found_assets:
            self.found_tags = self.Models.find_tags_by_asset_list(self.found_assets)

    def notify_observers(self):
        for x in self._observers:
            x.current_state_changed()

    def temp_asset_filling(self):
        self.ui.name_lineEdit.setText("shotgan")
        self.ui.tag_lineEdit.setText("weapon gun shoot")
        self.ui.path_lineEdit.setText('U:/AssetStorage/library/weapon/shotgan_ast')
        self.ui.image_lineEdit.setText("D:/work/_pythonProjects/asset_manager/images/im_07.PNG")
        text = "A weapon incorporating a metal tube"
        self.ui.description_textEdit.setPlainText(text)

        scenes = ["D:/work/_pythonProjects/asset_manager/main.py", "D:/work/_pythonProjects/asset_manager/test.py"]
        self.ui.file_list_widget.files_list = scenes


        gallery = ["D:/work/_pythonProjects/asset_manager/images/im_08.PNG ",
                   "D:/work/_pythonProjects/asset_manager/images/im_09.PNG "]
        self.ui.gallery_list_widget.files_list = gallery




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
