import json
import os
import queue
import re
import sys
import tempfile

from PyQt5 import QtCore
from PyQt5.QtCore import QSettings, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QCursor
from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QApplication

from UI.AssetWidget import AssetWidget
from UI.CustomTitleBar import CustomTitleBar
from UI.FileListWidget import FileListWidget, BasketWidget
from UI.GalleryWidget import GalleryWidget
from UI.TagButton import TagButton
from UI.TagsWidget import TagsWidget
from UI.TreeAssetsWidget import MenuTreeWidget
from UI.Ui_MainWindow import Ui_MainWindow
from UI.Ui_function import UiFunction
from Utilities.Logging import logger
from Utilities.Utilities import convert_path_to_global, remove_non_unique_tags, CopyWithProgress
from settings import COLUMN_WIDTH, SPACING, START_WINDOW_SIZE, SFX, FONT_SIZE, VERSION, ICON_FORMATS_PATTERN, \
    ASSETS_IN_ONE_STEP


class BaseThread(QtCore.QThread):
    def __init__(self, queue, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue

    def run(self):
        while True:
            func = self.queue.get()  # Get task
            if func:
                func()  # Run input function
                self.queue.task_done()


class ThreadQueue:
    """
    Creates a separate thread with a queue in which functions are dropped
    """
    def __init__(self):
        self.queue = queue.Queue()  # Create a queue
        self.threads = []
        self.thread = BaseThread(self.queue)
        self.threads.append(self.thread)

    def add_task(self, func):
        self.queue.put(func)


class MainWindow(QMainWindow, Ui_MainWindow, UiFunction, CustomTitleBar, ThreadQueue):
    """
    Functionality for the interface generated by the designer.
    Various custom widgets are installed here
    Main function for customizing interface

    UiFunction - functions for customizing the interface, animation, changing icons, etc.
    CustomTitleBar - remove TitleBar, setup user ones
    ThreadQueue - Creates a separate thread with a queue in which functions are dropped
    """
    def __init__(self, in_controller, parent=None):
        super(QMainWindow, self).__init__(parent)

        # set custom titleBar and thread
        CustomTitleBar.__init__(self)
        ThreadQueue.__init__(self)

        # there are two states of the assets menu
        self.__asset_menu_mode = "Add"

        # in edit mod save current asset id
        self.current_asset = None

        self.Controller = in_controller
        self.setupUi(self)
        self.window_label.setText("Asset browser  " + VERSION)

        # window scale setup
        self.add_window_scale()

        # name verification
        self.name_lineEdit.setValidator(QRegExpValidator(QRegExp("[-A-z0-9]+")))
        self.path_lineEdit.setValidator(QRegExpValidator(QRegExp("[-/A-z0-9]+")))
        self.add_dir_line_edit.setValidator(QRegExpValidator(QRegExp("[-/A-z0-9]+")))

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
        self.gallery_list_widget = FileListWidget(self.Controller, self.gallery_list)
        self.galery_frame_verticalLayout.insertWidget(1, self.gallery_list_widget)

        # insert content widget
        self.content_list = []
        self.file_list_widget = FileListWidget(self.Controller, self.content_list)
        self.scens_framelLayout.insertWidget(2, self.file_list_widget)

        # insert basket widget
        self.out_asset_list = []
        self.basket_list_widget = BasketWidget(self.Controller, self.out_asset_list)
        self.basket_list_widget.update_gallery = True
        self.basket_layout.insertWidget(0, self.basket_list_widget)

        # connect Ui to functions
        self.search_button.clicked.connect(self.Controller.refresh_ui)
        self.search_lineEdit.returnPressed.connect(self.Controller.refresh_ui)
        self.add_dir_button.clicked.connect(self.tree_widget.add_directory)
        self.add_dir_line_edit.returnPressed.connect(self.tree_widget.add_directory)
        self.expand_button.clicked.connect(lambda: self.switch_pages(0))
        self.tree_button.clicked.connect(lambda: self.switch_pages(1))
        self.settings_button.clicked.connect(lambda: self.switch_pages(2))
        self.gallery_button.clicked.connect(lambda: self.switch_pages(3))
        self.cart_button.clicked.connect(lambda: self.switch_pages(4))
        self.callaps_btn_a.clicked.connect(lambda: self.expand_close_animation("close"))
        self.callaps_btn_b.clicked.connect(lambda: self.expand_close_animation("close"))
        self.callaps_btn_c.clicked.connect(lambda: self.expand_close_animation("close"))
        self.callaps_btn_d.clicked.connect(lambda: self.expand_close_animation("close"))
        self.callaps_btn_e.clicked.connect(lambda: self.expand_close_animation("close"))
        self.path_Button.clicked.connect(self.add_path_btn)
        self.image_Button.clicked.connect(self.add_image_btn)
        self.scens_Button.clicked.connect(self.add_scenes_btn)
        self.galery_button.clicked.connect(self.add_gallery_btn)
        self.db_path_button.clicked.connect(self.add_db_path_btn)
        self.btn_close.clicked.connect(self.close)
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_maximize.clicked.connect(self.maximize_restore)
        self.font_spinBox.valueChanged.connect(self.set_font_size)
        self.erase_basket_button.clicked.connect(self.erase_basket)
        self.export_basket_button.clicked.connect(self.basket_list_widget.export_assets)
        self.gallery.scroll_bar_signal.connect(self.loading_assets_on_scroll)

        self.maximize = False  # application size state
        self.copy_progress_bar.hide()  # hide progress bar
        self.settings = None  # object for save settings
        self.load_settings()
        self.decorate_icons_color()

        # add contrext menu
        self.image_lineEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_lineEdit.customContextMenuRequested.connect(self.icon_line_edit_context_menu)
        
        self.copy_function = CopyWithProgress()
        self.copy_function.progress_bar_signal.connect(self.progress_bar_slot)
        self.thread.start()

        if not self.Controller.connect_db:
            self.status_message("Problems connecting to the database.", state="ERROR")
        logger.debug("Ui loaded successfully.\n")
        
    def progress_bar_slot(self, percent):
        if percent <= 100:
            self.copy_progress_bar.setValue(percent)
            
    def icon_line_edit_context_menu(self):
        """
        creates a context menu that allows you to insert an image from a clipboard
        """
        menu = QMenu()
        menu.setStyleSheet("""background-color: #16191d; color: #fff;""")
        menu.addAction(QAction("Paste from clipboard", self))
        action = menu.exec_(QCursor().pos())
        if action and action.text() == "Paste from clipboard":
            clipboard = QApplication.clipboard()
            icon = clipboard.image()
            if icon:
                file_path = os.path.join(tempfile.gettempdir(), 'tmp_image.png')
                result = icon.save(file_path)
                if result:
                    file_path = file_path.replace("\\", "/")
                    self.image_lineEdit.setText(file_path)
                    self.Controller.ui.status_message("Image added successfully")
                else:
                    self.Controller.ui.status_message("Information on the clipboard is not an image", state="ERROR")

    @property
    def asset_menu_mode(self):
        return self.__asset_menu_mode

    @asset_menu_mode.setter
    def asset_menu_mode(self, mode):
        """
        Changes the properties of buttons and labels when switching menu modes Create / Edit
        """
        self.add_asset_button.disconnect()
        self.erase_button.disconnect()
        if mode == "Add":
            self.clear_form()
            self.__asset_menu_mode = "Add"
            self.asset_menu_label.setText("Add Asset")
            self.add_asset_button.setText("Create")
            self.add_asset_button.clicked.connect(self.Controller.create_asset)
            self.erase_button.clicked.connect(self.clear_form)
            self.decorate_icon(self.add_asset_button, "file-plus.svg")
            self.current_asset = None

        else:  # mode="Edit"
            logger.debug("\n\n__________________Set edit mode___________________")
            self.__asset_menu_mode = "Edit"
            # open edit menu
            if self.drop_menu.width() == 0:
                self.expand_close_animation("expand")
            self.drop_stackedWidget.setCurrentIndex(0)
            self.decorate_buttons_background(0)
            self.asset_menu_label.setText("Edit")
            self.add_asset_button.setText("Ok")
            self.add_asset_button.clicked.connect(self.Controller.edit_asset)
            self.erase_button.clicked.connect(self.discard_edit)
            self.decorate_icon(self.add_asset_button, "edit.svg")
            self.Controller.ui.status_message("Edit mode activated")

    def current_state_changed(self):
        """
        Run in Controller.notify_observers as reacting to changes in current tags list
        """
        try:
            self.asset_menu_mode = "Add"
            self.update_assets_widgets()
            self.update_tags_widgets()
            self.tree_widget.update_ui()
            self.status_message(f"In the database were found {len(self.Controller.found_assets)} items ")
        except Exception as message:
            logger.error(message)

    def update_assets_widgets(self):
        """
        Updates rendered assets after searching
        """
        self.gallery.clear()
        if self.Controller.found_assets:
            for asset in self.Controller.found_assets[:ASSETS_IN_ONE_STEP]:
                asset_widget = AssetWidget(asset, self.Controller, width=COLUMN_WIDTH)
                self.gallery.add_widget(asset_widget)

    def loading_assets_on_scroll(self):
        """
        Staged loading of assets function
        """
        try:
            found_assets_num = len(self.Controller.found_assets)
            widget_num = len(self.gallery.widget_list)
            for i in range(widget_num, widget_num+ASSETS_IN_ONE_STEP):
                if len(self.gallery.widget_list)<found_assets_num:
                    asset = self.Controller.found_assets[i]
                    asset_widget = AssetWidget(asset, self.Controller, width=COLUMN_WIDTH)
                    self.gallery.add_widget(asset_widget)
        except Exception as message:
            logger.error(message)

    def update_tags_widgets(self):
        """
        Updates rendered tags buttons after searching
        """
        self.tag_widget.clear()
        if self.Controller.found_tags:
            for each_tag in self.Controller.found_tags:
                tag_widget = TagButton(each_tag, self.Controller)
                self.tag_widget.add_widget(tag_widget)

    def get_asset_data(self):
        """
        Reading menu fields when creating/editing asset
        """
        out_dict = dict()
        out_dict['name'] = self.name_lineEdit.text()
        out_dict['path'] = self.path_lineEdit.text()

        if out_dict['name'] and out_dict['path']:
            out_dict['asset_id'] = self.current_asset
            out_dict['path'] = convert_path_to_global(out_dict['path']) + "/" + out_dict['name'] + SFX

            icon = self.image_lineEdit.text()
            out_dict['icon'] = icon if re.search(ICON_FORMATS_PATTERN, icon) else ""

            out_dict['description'] = self.description_textEdit.toPlainText()

            # get a list of tags
            out_dict['tags'] = re.findall(r'[-0-9A-z_]+', self.tag_lineEdit.text())
            out_dict['tags'] = remove_non_unique_tags(out_dict['tags'])  # make tags uniqueness

            # get a list of scenes paths
            out_dict['scenes'] = self.file_list_widget.get_list()

            # get a list of gallery paths and verify it
            out_dict['gallery'] = [x for x in self.gallery_list_widget.get_list() if re.search(ICON_FORMATS_PATTERN, x)]

            logger.debug(json.dumps(out_dict))
            return out_dict
        else:
            self.status_message("One of the required fields is not filled", state="ERROR")
            logger.error("One of the required fields is not filled")
            return None

    def discard_edit(self):
        """
        Edit mode cancel button
        """
        self.asset_menu_mode = "Add"
        self.status_message("")
        self.clear_form()

    def load_settings(self):
        """
        If settings not exist - load default settings
        """
        # set default settings
        self.drop_menu.setFixedWidth(0)
        self.resize(*START_WINDOW_SIZE)

        file_path = os.path.join(tempfile.gettempdir(), 'asset_manager_settings.ini')
        has_settings = os.path.exists(file_path)
        self.settings = QSettings(file_path, QSettings.IniFormat)

        if self.settings.contains("ui settings"):
            self.search_lineEdit.setText(self.settings.value("ui settings"))
        if self.settings.contains("db settings"):
            self.db_path_lineEdit.setText(self.settings.value("db settings"))
        if self.settings.contains("ui pos"):
            self.move(self.settings.value("ui pos"))
        if self.settings.contains("font size"):
            self.font_spinBox.setValue(int(self.settings.value("font size")))
        else:
            self.font_spinBox.setValue(FONT_SIZE)

        if has_settings:
            logger.info("Settings loaded from file : " + file_path)

    def closeEvent(self, evt):
        """
        When window closed it save fields settings
        """
        logger.debug("\n\n__________________Close button clicked___________________")
        self.settings.setValue("ui settings", self.search_lineEdit.text())
        self.settings.setValue("db settings", self.db_path_lineEdit.text())
        self.settings.setValue("ui pos", self.pos())
        self.settings.setValue("font size", self.font_spinBox.value())
        logger.debug("Settings saved")
