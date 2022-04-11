import os
import tempfile

from PyQt5.QtCore import QVariantAnimation, QSettings, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QWidget, QSizeGrip, qApp

from Utilities.Logging import logger
from Utilities.Utilities import convert_path_to_local
from settings import DROP_MENU_WIDTH, COLUMN_WIDTH


class UiFunction(QWidget):
    """
    Functions for customizing the interface, animation, changing icons, etc.
    """

    def add_db_path_btn(self):
        lib_path = QFileDialog.getExistingDirectory(self, directory=self.Controller.lib_path)
        lib_path = lib_path.replace("\\", "/")
        self.db_path_lineEdit.setText(lib_path)
        self.Controller.lib_path = lib_path
        self.Controller.connect_db = self.Controller.Models.initialize(lib_path)
        if self.Controller.connect_db:
            self.Controller.refresh_ui()
        file_path = os.path.join(tempfile.gettempdir(), 'asset_manager_settings.ini')
        settings = QSettings(file_path, QSettings.IniFormat)
        settings.setValue("db settings", lib_path)
        logger.debug("New lib path : " + self.Controller.lib_path)

    def switch_pages(self, page):
        """
        toggles the left menu between add/edit asset, library try, asset overview and settings modes
        """
        self.decorate_buttons_background(page)
        if self.drop_menu.width() == 0:
            self.expand_close_animation("expand")
        else:
            if self.drop_stackedWidget.currentIndex() == page:
                self.expand_close_animation("close")
                self.decorate_buttons_background(page, color="#16191d")
        self.drop_stackedWidget.setCurrentIndex(page)

    def decorate_buttons_background(self, page, color="#343b47"):
        buttons = {0: self.expand_button, 1: self.tree_button, 3: self.gallery_button, 2: self.settings_button,
                   4: self.cart_button}
        for i in [0, 1, 3, 2, 4]:
            buttons[i].setStyleSheet("background-color: #16191d;")
            if i == page:
                buttons[i].setStyleSheet("background-color:" + color + ";")

    def decorate_icons_color(self):
        btn_dict = {self.expand_button: "file-plus.svg",
                    self.tree_button: "tree2.png",
                    self.gallery_button: "image.svg",
                    self.cart_button: "shopping-cart.svg",
                    self.settings_button: "settings.svg",
                    self.path_Button: "folder.svg",
                    self.db_path_button: "folder.svg",
                    self.image_Button: "folder.svg",
                    self.galery_button: "file-plus.svg",
                    self.scens_Button: "file-plus.svg",
                    self.add_asset_button: "file-plus.svg",
                    self.erase_button: "x-square.svg",
                    self.search_button: "search.svg",
                    self.callaps_btn_a: "x-circle.svg",
                    self.callaps_btn_b: "x-circle.svg",
                    self.callaps_btn_c: "x-circle.svg",
                    self.callaps_btn_d: "x-circle.svg",
                    self.add_dir_button: "folder-plus.svg",
                    self.tag_widget.left_button: "chevrons-left.svg",
                    self.tag_widget.right_button: "chevrons-right.svg",
                    self.erase_basket_button: "x-square.svg",
                    self.export_basket_button: "file.svg",
                    }
        for button in btn_dict:
            self.decorate_icon(button, btn_dict[button])

    @staticmethod
    def decorate_icon(button, icon):
        def enterEvent(event):
            button.setIcon(QIcon(":/icons_blue/icon_blue/" + icon))

        def leaveEvent(event):
            button.setIcon(QIcon(":/icons/icons/" + icon))

        button.enterEvent = enterEvent
        button.leaveEvent = leaveEvent
        button.setIcon(QIcon(":/icons/icons/" + icon))

    def expand_close_animation(self, action="expand"):
        if action == "expand":
            start, end = 0, DROP_MENU_WIDTH
            self.setMinimumWidth(DROP_MENU_WIDTH + COLUMN_WIDTH + 100)
        else:
            start, end = DROP_MENU_WIDTH, 0
            self.setMinimumWidth(COLUMN_WIDTH + 100)
        self.ani = QVariantAnimation()
        self.ani.setStartValue(start)
        self.ani.setEndValue(end)
        self.ani.setDuration(300)
        self.ani.valueChanged.connect(lambda value: self.drop_menu.setFixedWidth(value))
        self.ani.start()

    def add_path_btn(self):
        """
        Add path to ui
        """
        file_name = QFileDialog.getExistingDirectory(self, directory=self.Controller.lib_path)
        if file_name:
            self.path_lineEdit.setText(convert_path_to_local(file_name))

    def add_image_btn(self):
        """
        Add icon path to ui
        """
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]
        file_name = file_name.replace("\\", "/")
        self.image_lineEdit.setText(file_name)

    def add_scenes_btn(self):
        """
        Add scenes paths to ui
        """
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]
        file_name = file_name.replace("\\", "/")
        if file_name:
            self.file_list_widget.add_file(file_name)

    def add_gallery_btn(self):
        """
        Add gallery images paths to ui
        """
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]
        file_name = file_name.replace("\\", "/")
        if file_name:
            self.gallery_list_widget.add_file(file_name)

    def clear_form(self):
        """
        Clears the menu for adding or modifying assets
        """
        for form in [self.name_lineEdit, self.image_lineEdit, self.tag_lineEdit,  # self.path_lineEdit,
                     self.description_textEdit, self.file_list_widget, self.gallery_list_widget]:
            form.clear()

    def status_message(self, message, state="INFO"):
        """
        displays error messages and results of actions in the status bar
        """
        self.status_label.setText(message)
        if state == "ERROR":
            self.status_label.setStyleSheet(" color: red;")
        else:
            self.status_label.setStyleSheet(" color: #838ea2;")

    def maximize_restore(self):
        """
        fullscreen and normal window size switcher
        """
        if self.maximize:
            self.maximize = False
            self.btn_maximize.setIcon(QIcon(":/icons/icons/square.svg"))
            self.showNormal()
        else:
            self.showMaximized()
            self.btn_maximize.setIcon(QIcon(":/icons/icons/normalise.png"))
            self.maximize = True

    def set_font_size(self):
        """
        sets the font size of the entire application
        """
        self.settings.setValue("font size", self.font_spinBox.value())
        headers_list = [self.window_label, self.status_label, self.asset_menu_label, self.lib_tree_label,
                        self.settings_label, self.asset_overview_label, self.tree_widget]
        for widget in qApp.allWidgets():
            try:
                size = self.font_spinBox.value()
                if widget in headers_list:
                    size += 2
                font = widget.font()
                font.setPointSize(size)
                widget.setFont(font)
            except:
                pass

    def add_window_scale(self):
        """
        add window scale handler
        """
        sizegrip = QSizeGrip(self)
        sizegrip.setStyleSheet("image: url(:/icons/icons//scale.png);")
        sizegrip.setFixedSize(30, 20)
        self.footer_layout.addWidget(sizegrip, 0, Qt.AlignBottom | Qt.AlignRight)

    def erase_basket(self):
        self.basket_list_widget.clear()
        self.update_assets_widgets()
