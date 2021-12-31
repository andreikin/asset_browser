# -*- coding: utf-8 -*-
import re

from PyQt5.QtWidgets import QDialog, QWidget, QFileDialog
from UI.Ui_AssetCreationDialog import Ui_AssetCreationDialog


class AssetCreationDialog(QDialog, Ui_AssetCreationDialog):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = self.setupUi(self)

        self.create_Button.clicked.connect(self.accept)
        self.close_Button.clicked.connect(self.reject)
        self.path_Button.clicked.connect(self.add_path_btn)
        self.image_Button.clicked.connect(self.add_image_btn)
        self.scens_Button.clicked.connect(self.add_scenes_btn)

    def add_path_btn(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]
        self.path_lineEdit.setText(file_name)

    def add_image_btn(self):
        pass
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0]+"\n"
        self.image_lineEdit.setText(file_name)

    def add_scenes_btn(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')[0] + "\n"
        current = self.scens_textEdit.toPlainText() + file_name
        self.scens_textEdit.setPlainText(current)

    def get_asset_data (self):
        out_dict = dict()
        out_dict['name'] = self.name_lineEdit.text()
        out_dict['path'] = self.path_lineEdit.text()
        out_dict['image'] = self.image_lineEdit.text()
        out_dict['tags'] = re.findall(r'[0-9A-z_]+', self.tag_lineEdit.text())
        out_dict['description'] = self.description_textEdit.toPlainText()
        out_dict['scenes'] = self.scens_textEdit.toPlainText()
        return out_dict
