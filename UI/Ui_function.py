from PyQt5.QtCore import QVariantAnimation
from PyQt5.QtWidgets import QFileDialog, QWidget

from Utilities.Logging import logger
from settings import DROP_MENU_WIDTH, SFX


class UiFunction(QWidget):

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
        asset_name = self.name_lineEdit.text()
        file_name = QFileDialog.getExistingDirectory(self, directory=self.Controller.lib_path)
        file_name = file_name.replace("\\", "/") + "/" + asset_name + SFX
        self.path_lineEdit.setText(file_name)

    def add_db_path_btn(self):
        file_name = QFileDialog.getSaveFileName(self, 'Save File', filter='*.db')[0]
        file_name = file_name.replace("\\", "/")
        self.db_path_lineEdit.setText(file_name)
        # TODO: add database reconnect or program restart

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

    def edit_path_when_input_name(self):
        """
        changes the path of the asset when the name is changed
        """
        path = self.path_lineEdit.text().split("/")[:-1]
        name = self.name_lineEdit.text()
        self.path_lineEdit.setText("/".join(path) + "/" + name + SFX)

    def status_message(self, message, state="INFO"):
        self.status_label.setText(message)
        if state == "ERROR":
            self.status_label.setStyleSheet(" color: red;")
        else:
            self.status_label.setStyleSheet(" color: #838ea2;")
