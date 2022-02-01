import json
import os
import re
import sys
import tempfile
from random import randint

from PyQt5.QtCore import QVariantAnimation, QSettings, Qt
from PyQt5.QtGui import QIcon, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QWidget, QLabel

from UI.AssetWidget import AssetWidget
from UI.CustomTitleBar import CustomTitleBar
from UI.FileListWidget import FileListWidget
from UI.GalleryWidget import GalleryWidget
from UI.TagButton import TagButton
from UI.TagsWidget import TagsWidget
from UI.TreeAssetsWidget import MenuTreeWidget
from UI.Ui_MainWindow import Ui_MainWindow
from UI.Ui_function import UiFunction
from Utilities.Logging import logger
from Utilities.Utilities import get_tags_from_path
from settings import COLUMN_WIDTH, SPACING, START_WINDOW_SIZE, SFX


class MainWindow(QMainWindow, Ui_MainWindow, UiFunction, CustomTitleBar,):
    def __init__(self, in_controller, parent=None):
        super(QMainWindow, self).__init__(parent)

        # set custom titleBar
        CustomTitleBar.__init__(self)

        # there are two states of the assets menu
        self.__asset_menu_mode = "Add"

        self.Controller = in_controller
        self.setupUi(self)
        self.drop_menu.setFixedWidth(0)
        self.resize(*START_WINDOW_SIZE)

        # insert Gallery widget
        self.gallery = GalleryWidget(icons_width=COLUMN_WIDTH, spacing=SPACING)
        self.galery_VLayout.addWidget(self.gallery)
        self.update_assets_widgets()

        # insert tags widget
        self.tag_widget = TagsWidget()
        self.tags_verticalLayout.addWidget(self.tag_widget)

        # insert tree widget
        self.tree_widget = MenuTreeWidget(self.Controller)
        self.tree_body_VLayout.addWidget(self.tree_widget)

        # insert gallery widget
        self.gallery_list = []
        self.gallery_list_widget = FileListWidget(self.gallery_list)
        self.galery_frame_verticalLayout.insertWidget(1, self.gallery_list_widget)

        # insert content widget
        self.content_list = []
        self.file_list_widget = FileListWidget(self.content_list)
        self.scens_framelLayout.insertWidget(1, self.file_list_widget)

        # connect Ui to functions
        self.search_button.clicked.connect(self.Controller.refresh_ui)
        self.search_lineEdit.returnPressed.connect(self.Controller.refresh_ui)
        self.add_dir_button.clicked.connect(self.tree_widget.add_directory)
        self.add_dir_line_edit.returnPressed.connect(self.tree_widget.add_directory)
        self.name_lineEdit.textChanged.connect(self.edit_path_when_input_name)
        self.expand_button.clicked.connect(lambda: self.switch_pages(0))
        self.tree_button.clicked.connect(lambda: self.switch_pages(1))
        self.settings_button.clicked.connect(lambda: self.switch_pages(2))
        self.info_button.clicked.connect(lambda: self.switch_pages(3))
        self.callaps_btn_a.clicked.connect(lambda: self.expand_close_animation("close"))
        self.callaps_btn_b.clicked.connect(lambda: self.expand_close_animation("close"))
        self.callaps_btn_c.clicked.connect(lambda: self.expand_close_animation("close"))
        self.callaps_btn_d.clicked.connect(lambda: self.expand_close_animation("close"))
        self.path_Button.clicked.connect(self.add_path_btn)
        self.image_Button.clicked.connect(self.add_image_btn)
        self.scens_Button.clicked.connect(self.add_scenes_btn)
        self.galery_button.clicked.connect(self.add_gallery_btn)
        self.db_path_button.clicked.connect(self.add_db_path_btn)
        self.btn_close.clicked.connect(self.close)
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_maximize.clicked.connect(self.showMaximized)

        self.asset_menu_mode = "Add"
        # object for save settings
        file_path = os.path.join(tempfile.gettempdir(), 'asset_manager_settings.ini')
        self.settings = QSettings(file_path, QSettings.IniFormat)
        self.load_settings()

        logger.debug("Ui loaded successfully.")

    @property
    def asset_menu_mode(self):
        return self.__asset_menu_mode

    @asset_menu_mode.setter
    def asset_menu_mode(self, mode):
        self.add_asset_button.disconnect()
        self.erase_button.disconnect()
        if mode == "Add":
            self.__asset_menu_mode = "Add"
            self.asset_menu_label.setText("Add Asset")
            self.erase_button.setText("Erase form")
            self.add_asset_button.setText("Add Asset")
            self.add_asset_button.clicked.connect(self.Controller.create_asset)
            self.erase_button.clicked.connect(self.clear_form)

            for le in [self.name_lineEdit, self.path_lineEdit]:
                le.setReadOnly(False)
                le.setStyleSheet("color:  #fff;")

            self.add_asset_button.setIcon(QIcon(":/icons/icons//file-plus.svg"))
            logger.debug(" Add mod")

        else:  # mode="Edit"
            self.__asset_menu_mode = "Edit"
            # open edit menu
            if self.drop_menu.width() == 0:
                self.expand_close_animation("expand")
            self.drop_stackedWidget.setCurrentIndex(0)
            self.asset_menu_label.setText("Edit Asset")
            self.erase_button.setText("Cancel")
            self.add_asset_button.setText("Edit")
            self.add_asset_button.clicked.connect(self.Controller.edit_asset)
            self.erase_button.clicked.connect(self.discard_edit)

            for le in [self.name_lineEdit, self.path_lineEdit]:
                le.setReadOnly(True)
                le.setStyleSheet("color:  #838ea2;"
                                 "background-color:#2c313c;")

            self.add_asset_button.setIcon(QIcon(":/icons/icons//edit.svg"))
            logger.debug(" Edit mod")

    def current_state_changed(self):
        self.asset_menu_mode = "Add"
        self.update_assets_widgets()
        self.update_tags_widgets()
        self.tree_widget.update_ui()
        self.status_message(f"In the database were found {len(self.Controller.found_assets)} items ")

    def update_assets_widgets(self):
        self.gallery.clear()
        if self.Controller.found_assets:
            for asset in self.Controller.found_assets:
                asset_widget = AssetWidget(asset, self.Controller, width=COLUMN_WIDTH)
                self.gallery.add_widget(asset_widget)
        logger.debug(" executed")

    def update_tags_widgets(self):
        self.tag_widget.clear()
        if self.Controller.found_tags:
            for each_tag in self.Controller.found_tags:
                tag_widget = TagButton(each_tag, self.Controller)
                self.tag_widget.add_widget(tag_widget)
        logger.debug(" executed")

    def get_asset_data(self):
        # get from ui
        out_dict = dict()
        out_dict['name'] = self.name_lineEdit.text().replace("_", " ")
        out_dict['tags'] = re.findall(r'[0-9A-z_]+', self.tag_lineEdit.text())
        logger.debug(self.path_lineEdit.text())
        logger.debug("/"+out_dict['name'].replace("_", " ")+SFX)
        if self.path_lineEdit.text() == "/"+out_dict['name']+SFX:
            self.status_message("Need to select the directory in which the asset will be", state="ERROR")
            return None

        out_dict['path'] = self.path_lineEdit.text()
        out_dict['icon'] = self.image_lineEdit.text()
        out_dict['description'] = self.description_textEdit.toPlainText()

        folders_tags = get_tags_from_path(out_dict['path'])
        out_dict['tags'] += folders_tags
        out_dict['tags'] = list(set(out_dict['tags']))  # make tags unic

        # get a list of scenes paths
        out_dict['scenes'] = self.file_list_widget.get_list()

        # get a list of gallery paths
        out_dict['gallery'] = self.gallery_list_widget.get_list()

        logger.debug(json.dumps(out_dict))
        if out_dict['name'] and out_dict['path']:
            return out_dict
        else:
            self.status_message("One of the required fields is not filled", state="ERROR")
            logger.error("One of the required fields is not filled")
            return None

    def discard_edit(self):
        self.asset_menu_mode = "Add"

    def load_settings(self):
        """
        If settings not exist - load default settings
        """
        if self.settings.contains("ui settings"):
            self.search_lineEdit.setText(self.settings.value("ui settings"))
        if self.settings.contains("db settings"):
            self.db_path_lineEdit.setText(self.settings.value("db settings"))
        if self.settings.contains("ui pos"):
            self.move(self.settings.value("ui pos"))

    def closeEvent(self, evt):
        """
        When window closed it save fields settings
        """
        self.settings.setValue("ui settings", self.search_lineEdit.text())
        self.settings.setValue("db settings", self.db_path_lineEdit.text())
        self.settings.setValue("ui pos", self.pos())
        logger.debug("Settings saved")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    for x in range(135):
        but = QPushButton()
        but.setFixedHeight(randint(50, 150))
        window.gallery.add_widget(but)

    window.show()
    app.exec_()
