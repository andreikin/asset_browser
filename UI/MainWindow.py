import os
import re
import sys
import tempfile
from random import randint

from PyQt5.QtCore import QVariantAnimation, QSettings
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog

from UI.AssetWidget import AssetWidget
from UI.GalleryWidget import GalleryWidget
from UI.TagWidget import TagWidget
from UI.TagsWidget import TagsWidget
from UI.Ui_MainWindow import Ui_MainWindow

COLUMN_WIDTH = 110
SPACING = 10


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, in_controller, parent=None):
        super(QMainWindow, self).__init__(parent)

        self.Controller = in_controller

        self.setupUi(self)
        self.drop_menu.setFixedWidth(0)

        # insert Gallery widget
        self.gallery = GalleryWidget(icons_width=COLUMN_WIDTH, spacing=SPACING)
        self.galery_VLayout.addWidget(self.gallery)
        self.add_assets_widgets()
        # insert tags widget
        self.tag_widget = TagsWidget()
        self.tags_verticalLayout.addWidget(self.tag_widget)

        # connect buttons
        self.expand_button.clicked.connect(lambda: self.switch_stacke_widget_pages(0))
        self.settings_button.clicked.connect(lambda: self.switch_stacke_widget_pages(1))
        self.info_button.clicked.connect(lambda: self.switch_stacke_widget_pages(2))

        self.callaps_btn_a.clicked.connect(lambda: self.expand_callaps_switch("close"))
        self.callaps_btn_b.clicked.connect(lambda: self.expand_callaps_switch("close"))
        self.callaps_btn_c.clicked.connect(lambda: self.expand_callaps_switch("close"))

        self.path_Button.clicked.connect(self.add_path_btn)
        self.image_Button.clicked.connect(self.add_image_btn)
        self.scens_Button.clicked.connect(self.add_scenes_btn)

        # object for save settings
        file_path = os.path.join(tempfile.gettempdir(), 'asset_manager_settings.ini')
        print(file_path)
        self.settings = QSettings(file_path, QSettings.IniFormat)
        self.load_settings()

    def current_state_changed(self):
        self.add_assets_widgets()
        self.add_tags_widgets()

    def add_assets_widgets(self):
        self.gallery.clear()
        if self.Controller.found_assets:
            for asset in self.Controller.found_assets:
                asset_widget = AssetWidget(asset, self.Controller.Models, width=COLUMN_WIDTH, height=randint(120, 200))
                self.gallery.add_widget(asset_widget)

    def add_tags_widgets(self):
        self.tag_widget.clear()
        if self.Controller.found_tags:
            for each_tag in self.Controller.found_tags:
                tag_widget = TagWidget(each_tag, self.Controller)
                self.tag_widget.add_widget(tag_widget)

    def switch_stacke_widget_pages(self, page):
        if self.drop_menu.width() == 0:
            self.expand_callaps_switch("expand")
        if self.stackedWidget.currentIndex() == page and not self.drop_menu.width() == 0:
            self.expand_callaps_switch("close")
        self.stackedWidget.setCurrentIndex(page)



    def expand_callaps_switch(self, action="expand"):
        if action == "expand":
            start, end = 0, 300
        else:
            start, end = 300, 0
        self.ani = QVariantAnimation()
        self.ani.setStartValue(start)
        self.ani.setEndValue(end)
        self.ani.setDuration(300)
        self.ani.valueChanged.connect(self.update_menu_width)
        self.ani.start()

    def update_menu_width(self, value):
        self.drop_menu.setFixedWidth(value)

    def add_path_btn(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]
        self.path_lineEdit.setText(file_name)

    def add_image_btn(self):
        pass
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0] + "\n"
        self.image_lineEdit.setText(file_name)

    def add_scenes_btn(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0] + "\n"
        current = self.scens_textEdit.toPlainText() + file_name
        self.scens_textEdit.setPlainText(current)

    def get_asset_data(self):
        out_dict = dict()
        out_dict['name'] = self.name_lineEdit.text()
        out_dict['path'] = self.path_lineEdit.text()
        out_dict['image'] = self.image_lineEdit.text()
        out_dict['tags'] = re.findall(r'[0-9A-z_]+', self.tag_lineEdit.text())
        out_dict['description'] = self.description_textEdit.toPlainText()
        out_dict['scenes'] = self.scens_textEdit.toPlainText()
        return out_dict


    def load_settings(self):
        """
        If settings not exist - load default settings
        """
        if self.settings.contains("ui settings"):
            self.search_lineEdit.setText(self.settings.value("ui settings"))

    def closeEvent(self, evt):
        """
        When window closed it save fields settings
        """
        current = self.search_lineEdit.text()
        self.settings.setValue("ui settings", current)
        print("settings saved")





if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    for x in range(135):
        but = QPushButton()
        but.setFixedHeight(randint(50, 150))
        window.gallery.add_widget(but)

    window.show()
    app.exec_()
