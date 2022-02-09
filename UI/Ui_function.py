import os
import tempfile

from PyQt5.QtCore import QVariantAnimation, QSettings
from PyQt5.QtWidgets import QFileDialog, QWidget

from Utilities.Logging import logger
from Utilities.Utilities import get_library_path, convert_path_to_local
from settings import DROP_MENU_WIDTH, SFX, DATABASE_NAME


class UiFunction(QWidget):

    def add_db_path_btn(self):
        lib_path = QFileDialog.getExistingDirectory(self, directory=self.Controller.lib_path)
        lib_path = lib_path.replace("\\", "/")
        # self.switch_to_db(lib_path)
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
        if self.drop_menu.width() == 0:
            self.expand_close_animation("expand")
        else:
            if self.drop_stackedWidget.currentIndex() == page:
                self.expand_close_animation("close")
        self.drop_stackedWidget.setCurrentIndex(page)

    def expand_close_animation(self, action="expand"):
        if action == "expand":
            start, end = 0, DROP_MENU_WIDTH
        else:
            start, end = DROP_MENU_WIDTH, 0
        self.ani = QVariantAnimation()
        self.ani.setStartValue(start)
        self.ani.setEndValue(end)
        self.ani.setDuration(300)
        self.ani.valueChanged.connect(lambda value: self.drop_menu.setFixedWidth(value))
        self.ani.start()

    def add_path_btn(self):
        file_name = QFileDialog.getExistingDirectory(self, directory=self.Controller.lib_path)
        if file_name:
            self.path_lineEdit.setText(convert_path_to_local(file_name))

    def add_image_btn(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]
        file_name = file_name.replace("\\", "/")
        self.image_lineEdit.setText(file_name)

    def add_scenes_btn(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]
        file_name = file_name.replace("\\", "/")
        if file_name:
            self.file_list_widget.add_file(file_name)

    def add_gallery_btn(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]
        file_name = file_name.replace("\\", "/")
        if file_name:
            self.gallery_list_widget.add_file(file_name)

    def clear_form(self):
        for form in [self.name_lineEdit, self.path_lineEdit, self.image_lineEdit, self.tag_lineEdit,
                     self.description_textEdit, self.file_list_widget, self.gallery_list_widget]:
            form.clear()

    def status_message(self, message, state="INFO"):
        self.status_label.setText(message)
        if state == "ERROR":
            self.status_label.setStyleSheet(" color: red;")
        else:
            self.status_label.setStyleSheet(" color: #838ea2;")

    def set_font_size(self):
        self.settings.setValue("font size", self.font_spinBox.value())
        headers_list = [self.window_label, self.status_label, self.asset_menu_label, self.lib_tree_label,
                        self.settings_label, self.asset_overview_label, self.tree_widget]
        for widget in self.Controller.application.allWidgets():
            try:
                size = self.font_spinBox.value()
                if widget in headers_list:
                    size += 2
                font = widget.font()
                font.setPointSize(size)
                widget.setFont(font)
            except:
                pass
