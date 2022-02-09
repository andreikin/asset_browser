# -*- coding: utf-8 -*-
import json
import os
import re
import shutil
import subprocess

import PyQt5
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QSize, QRect, QEvent, QMimeData, QUrl
from PyQt5.QtGui import QCursor, QDrag, QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFrame, QSizePolicy, QApplication, QAction, QMenu, \
    QMessageBox, QHBoxLayout, QLabel, QListWidget, QAbstractItemView, QGraphicsItem

from Asset import Asset
from Models import Models
from Utilities.Logging import logger
from Utilities.Utilities import get_library_path, convert_path_to_local, set_font_size
from settings import COLUMN_WIDTH, DROP_MENU_WIDTH, DATABASE_NAME

BTN_WIDTH = 30  # The size of the buttons inside the widget
ICON_SIZE = 22  # The size of the icon in it


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

        self.open_button = QPushButton("", parent=self.frame_shadow)
        self.open_button.clicked.connect(self.open_directory)

        self.open_button.setGeometry(self.places_buttons_by_x()[0], self.height - 35, BTN_WIDTH, BTN_WIDTH)
        self.open_button.setIcon(QIcon(":/icons/icons//folder.svg"))
        self.open_button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.open_button.setStyleSheet("background-color: #16191d;"
                                       "border-radius: " + str(BTN_WIDTH / 2) + "px;")

        self.edit_button = QPushButton("", parent=self.frame_shadow)
        self.edit_button.clicked.connect(self.preparation_for_editing)
        self.edit_button.setGeometry(self.places_buttons_by_x()[1], self.height - 35, BTN_WIDTH, BTN_WIDTH)
        self.edit_button.setIcon(QIcon(":/icons/icons/edit.svg"))
        self.edit_button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.edit_button.setStyleSheet("background-color: #16191d;"
                                       "border-radius: " + str(BTN_WIDTH / 2) + "px;")

        self.del_button = QPushButton("", parent=self.frame_shadow)
        self.del_button.clicked.connect(self.delete_asset)
        self.del_button.setGeometry(self.places_buttons_by_x()[2], self.height - 35, BTN_WIDTH, BTN_WIDTH)
        self.del_button.setIcon(QIcon(":/icons/icons/x-circle.svg"))
        self.del_button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.del_button.setStyleSheet("background-color: #16191d;"
                                      "border-radius: " + str(BTN_WIDTH / 2) + "px;")

        self.hidden_list = [self.ast_label, self.edit_button, self.del_button, self.open_button]
        if not self.db_asset.icon:
            self.frame_shadow.setIcon(QIcon(":/icons/icons/camera-off.svg"))
            self.frame_shadow.setIconSize(QtCore.QSize(25, 25))
            self.hidden_list.pop(0)  # liable not hiding
        self.outside_event()

        # set font size
        size = self.Controller.ui.font_spinBox.value()
        set_font_size(self.ast_label, size)

        # connect Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.right_click_handler)

    def asset_overview(self):
        """
        starts the widget gallery view
        """

        # If the selected asset is not loaded, it  loaded otherwise the menu is collapsed
        if self == AssetWidget.current_asset and self.Controller.ui.drop_menu.width() != 0 and self.Controller.ui.drop_stackedWidget.currentIndex() == 3:
            self.Controller.ui.expand_close_animation("close")
            AssetWidget.current_asset = None
            logger.debug("None")

        self.Controller.ui.drop_stackedWidget.setCurrentIndex(3)
        if self.Controller.ui.drop_menu.width() == 0:
            self.Controller.ui.expand_close_animation("expand")

        self.Controller.ui.asset_overview_label.setText(" View asset " + self.db_asset.name)
        asset_data = Asset.recognize_asset(self.db_asset.path)
        self.Controller.ui.description_textEdit2.setPlainText(asset_data["description"])
        if not asset_data["description"]:
            self.Controller.ui.description_textEdit2.hide()
        else:
            self.Controller.ui.description_textEdit2.show()
            lines_num = len(asset_data["description"]) / 40
            self.Controller.ui.description_textEdit2.setFixedHeight(lines_num * 17 + 17)

        for i in range(self.Controller.ui.gallery_VLayout.count()):
            widget = self.Controller.ui.gallery_VLayout.itemAt(i).widget()
            if type(widget) == PyQt5.QtWidgets.QFrame:
                widget.deleteLater()

        for image_path in asset_data["gallery"]:
            self.frame_image = QFrame()
            pix = QPixmap(image_path)
            pix = pix.scaledToWidth(DROP_MENU_WIDTH - 45, mode=Qt.SmoothTransformation)
            self.frame_image.setFixedSize(pix.width(), pix.height())
            self.Controller.ui.gallery_VLayout.insertWidget(1, self.frame_image)
            self.frame_image.setStyleSheet("border-radius: 6px;"
                                           "background-color: #2c313c;"
                                           "border-image: url(" + image_path + ") 3 10 3 10;}")

        logger.debug(self.db_asset.name + "\n")
        AssetWidget.current_asset = self

    def places_buttons_by_x(self, offset=0.05):
        """
        places three buttons on the x-axis
        """
        dist = COLUMN_WIDTH * offset
        widget_centre = COLUMN_WIDTH / 2
        return [widget_centre - BTN_WIDTH - BTN_WIDTH / 2 - dist,
                widget_centre - BTN_WIDTH / 2,
                widget_centre + BTN_WIDTH / 2 + dist]

    def height_calculation(self, ):
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

        pattern = r"_ast$"
        asset_data['name'] = re.sub(pattern, "", asset_data['name'])

        self.Controller.ui.name_lineEdit.setText(asset_data['name'])
        self.Controller.ui.tag_lineEdit.setText(" ".join(asset_data['tags']))

        self.Controller.ui.path_lineEdit.setText(convert_path_to_local(asset_data['path']))
        self.Controller.ui.image_lineEdit.setText(asset_data['icon'])
        self.Controller.ui.description_textEdit.setPlainText(asset_data['description'])
        self.Controller.ui.file_list_widget.clear()
        self.Controller.ui.file_list_widget.add_files_list(asset_data['scenes'])
        self.Controller.ui.gallery_list_widget.clear()
        self.Controller.ui.gallery_list_widget.add_files_list(asset_data['gallery'])
        logger.debug("fill in the fields for editing\n")

    def delete_asset(self):
        dialog_message = "Delete asset", "Are you sure \nyou want to delete \nasset?"
        dialog = QMessageBox(QMessageBox.Critical, *dialog_message, buttons=QMessageBox.Ok | QMessageBox.Cancel)
        dialog.setStyleSheet("""background-color: #16191d; color: #fff;""")
        dialog_result = dialog.exec()
        if dialog_result == 1024:
            asset_data = Asset.recognize_asset(self.db_asset.path)
            Asset(self.Controller, **asset_data).delete_asset()


if __name__ == "__main__":
    import sys


    class MyWindow(QWidget):
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            self.vbox = QVBoxLayout()
            self.db_path = get_library_path() + "/" + DATABASE_NAME
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
