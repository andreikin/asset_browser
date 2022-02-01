# -*- coding: utf-8 -*-
import json
import os
import re
import shutil
import subprocess

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QSize, QRect, QEvent, QMimeData, QUrl
from PyQt5.QtGui import QCursor, QDrag, QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFrame, QSizePolicy, QApplication, QAction, QMenu, \
    QMessageBox, QHBoxLayout, QLabel, QListWidget, QAbstractItemView, QGraphicsItem

from Asset import Asset
from Models import Models
from Utilities.Logging import logger
from Utilities.Utilities import get_db_path


class AssetWidget(QWidget):
    current_asset = None

    def __init__(self, db_asset, in_controller, parent=None, width=100):
        QWidget.__init__(self, parent)
        self.db_asset = db_asset  # asset object from database
        self.Controller = in_controller
        self.width = width
        self.height = self.height_calculation()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.frame_image = QFrame()
        self.frame_image.setObjectName("frame_image")
        self.frame_image.setFixedSize(self.width, self.height)
        self.layout.addWidget(self.frame_image)
        self.frame_image.setStyleSheet("border-radius: 12px;"
                                       "background-color: #2c313c;"
                                       "border-image: url(" + self.db_asset.icon + ") 3 10 3 10;}")

        self.frame_shadow = QPushButton(parent=self)
        self.frame_shadow.clicked.connect(self.asset_overview)
        self.frame_shadow.setObjectName("frame_shadow")
        self.frame_shadow.setGeometry(0, 0, self.width, self.height)
        self.frame_shadow.installEventFilter(self)

        self.ast_label = QLabel(self.db_asset.name, parent=self.frame_shadow)
        self.ast_label.setGeometry(10, 10, self.width - 20, 22)
        self.ast_label.setStyleSheet("background-color: #16191d;"
                                     "border-radius: 10px;"
                                     "padding: 0 10px;"
                                     "color: #fff;")
        BTN_RAD = 30
        ICON_SIZE = 22
        self.edit_button = QPushButton("", parent=self.frame_shadow)
        self.edit_button.clicked.connect(self.preparation_for_editing)
        self.edit_button.setGeometry(self.width / 2 - BTN_RAD / 2, self.height - 35, BTN_RAD, BTN_RAD)
        self.edit_button.setIcon(QIcon(":/icons/icons/edit.svg"))
        self.edit_button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.edit_button.setStyleSheet("background-color: #16191d;"
                                       "border-radius: " + str(BTN_RAD / 2) + "px;")

        self.del_button = QPushButton("", parent=self.frame_shadow)
        self.del_button.clicked.connect(self.delete_asset)
        self.del_button.setGeometry(self.width - BTN_RAD - 6, self.height - 35, BTN_RAD, BTN_RAD)
        self.del_button.setIcon(QIcon(":/icons/icons/x-circle.svg"))
        self.del_button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.del_button.setStyleSheet("background-color: #16191d;"
                                      "border-radius: " + str(BTN_RAD / 2) + "px;")

        self.open_button = QPushButton("", parent=self.frame_shadow)
        self.open_button.clicked.connect(self.open_directory)
        self.open_button.setGeometry(6, self.height - 35, BTN_RAD, BTN_RAD)
        self.open_button.setIcon(QIcon(":/icons/icons//folder.svg"))
        self.open_button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.open_button.setStyleSheet("background-color: #16191d;"
                                       "border-radius: " + str(BTN_RAD / 2) + "px;")

        self.hidden_list = [self.ast_label, self.edit_button, self.del_button, self.open_button]
        if not self.db_asset.icon:
            self.frame_shadow.setIcon(QIcon(":/icons/icons/camera-off.svg"))
            self.frame_shadow.setIconSize(QtCore.QSize(25, 25))
            self.hidden_list.pop(0)  # liable not hiding
        self.outside_event()

        # connect Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.right_click_handler)

    def asset_overview(self):
        """
        starts the widget gallery view
        """
        self.Controller.ui.drop_stackedWidget.setCurrentIndex(3)
        if not self == self.current_asset:
            if self.Controller.ui.drop_menu.width() == 0:
                self.Controller.ui.expand_close_animation("expand")
            self.Controller.ui.help_text_label.setText(" The current asset is " + self.db_asset.name)
            logger.debug(self.db_asset.name)
            AssetWidget.current_asset = self
        else:
            self.Controller.ui.expand_close_animation("close")
            AssetWidget.current_asset = None
            logger.debug("None")

    def height_calculation(self):
        pix = QPixmap(self.db_asset.icon)
        try:
            return pix.height() / (pix.width() / self.width)
        except ZeroDivisionError:
            return self.width * 1.5

    def mouseMoveEvent(self, e):
        """
        drag and drop settings
        """
        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setUrls([QUrl.fromLocalFile(self.db_asset.path), ])
        pix = QPixmap(":/icons/icons/file.svg")
        drag.setPixmap(pix.scaledToWidth(24, Qt.SmoothTransformation))
        drag.setMimeData(mimedata)
        res = drag.exec_(Qt.CopyAction)

    def eventFilter(self, obj, event):
        """
         changes the appearance of the widget when the mouse pointer is outside or inside
         """
        if event.type() == QEvent.HoverEnter:
            self.inside_event()
        elif event.type() == QEvent.HoverLeave:
            self.outside_event()
        return super(AssetWidget, self).eventFilter(obj, event)

    def inside_event(self):
        for elem in self.hidden_list:
            elem.show()
        self.frame_shadow.setStyleSheet("background-color: rgba(0, 0, 0, 100);"
                                        "border-radius: 12px;")

    def outside_event(self):
        self.frame_shadow.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        for elem in self.hidden_list:
            elem.hide()

    # def right_click_handler(self, pos):
    #     menu = QMenu()
    #     menu.setStyleSheet("""background-color: #16191d; color: #fff;""")
    #     menu.addAction(QAction(self.db_asset.name, self))
    #     menu.addSeparator()
    #     menu.addAction(QAction("Open in explorer", self))
    #     menu.addAction(QAction("Edit asset", self))
    #     menu.addAction(QAction("Delete asset", self))
    #     action = menu.exec_(QCursor().pos())
    #     if action:
    #         if action.text() == "Open in explorer":
    #             subprocess.run(['explorer', os.path.realpath(self.db_asset.path)])
    #         elif action.text() == "Delete asset":
    #             self.delete_asset()
    #         elif action.text() == "Edit asset":
    #             self.preparation_for_editing()
    #     self.outside_event()

    def open_directory(self):
        subprocess.run(['explorer', os.path.realpath(self.db_asset.path)])

    def preparation_for_editing(self):
        """
        change the menu mode and fill in the fields for editing
        """
        self.Controller.ui.asset_menu_mode = "Edit"
        asset_data = Asset.recognize_asset(self.db_asset.path)
        self.Controller.ui.name_lineEdit.setText(asset_data['name'])
        self.Controller.ui.tag_lineEdit.setText(" ".join(asset_data['tags']))
        self.Controller.ui.path_lineEdit.setText(asset_data['path'])
        self.Controller.ui.image_lineEdit.setText(asset_data['icon'])
        self.Controller.ui.description_textEdit.setPlainText(asset_data['description'])
        self.Controller.ui.file_list_widget.clear()
        self.Controller.ui.file_list_widget.add_files_list(asset_data['scenes'])
        self.Controller.ui.gallery_list_widget.clear()
        self.Controller.ui.gallery_list_widget.add_files_list(asset_data['gallery'])

        #self.Controller.ui.gallery_list_widget.files_list = asset_data['gallery']


        logger.debug("fill in the fields for editing\n")

    def delete_asset(self):
        dialog_message = "Delete asset", "Are you sure \nyou want to delete \nasset?"
        dialog = QMessageBox(QMessageBox.Critical, *dialog_message, buttons=QMessageBox.Ok | QMessageBox.Cancel)
        dialog.setStyleSheet("""background-color: #16191d; color: #fff;""")
        dialog_result = dialog.exec()
        if dialog_result == 1024:
            process_result = self.Controller.Models.delete_asset(self.db_asset)
            if not process_result:
                self.Controller.ui.status_message("information from the database was not deleted", state="ERROR")
            else:
                try:
                    shutil.rmtree(self.db_asset.path)
                    logger.debug("Asset " + self.db_asset.name + " deleted successfully")
                    self.Controller.ui.status_message("Asset " + self.db_asset.name + " deleted successfully")
                except Exception as message:
                    logger.error(message)
                    self.Controller.ui.status_message("An error occurred and the asset was not correctly deleted",
                                                      state="ERROR")
            self.Controller.refresh_ui()


if __name__ == "__main__":
    import sys


    class MyWindow(QWidget):
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            self.vbox = QVBoxLayout()
            self.db_path = get_db_path()
            Models.initialize(self.db_path)
            db_asset = Models.find_assets_by_tag_list(["orange", ])[0]
            self.asset = AssetWidget(db_asset, Models)

            self.vbox.addWidget(self.asset)
            self.setLayout(self.vbox)


    app = QApplication(sys.argv)
    window = MyWindow()
    window.resize(500, 300)
    window.show()
    sys.exit(app.exec_())
