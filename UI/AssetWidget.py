# -*- coding: utf-8 -*-
import json
import os
import re
import subprocess

import PyQt5
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QEvent, QMimeData, QUrl
from PyQt5.QtGui import QDrag, QPixmap, QIcon, QCursor
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFrame, QApplication, QMessageBox, QLabel, QMenu, \
    QAction, QCheckBox

from Asset import Asset
from Models import Models
from UI.Ui_function import UiFunction
from Utilities.Logging import logger
from Utilities.telegram_bot import send_message_to_bot
from Utilities.Utilities import get_library_path, convert_path_to_local, set_font_size, get_preview_images
from settings import COLUMN_WIDTH, DROP_MENU_WIDTH, DATABASE_NAME

BTN_WIDTH = 30  # The size of the buttons inside the widget
ICON_SIZE = 22  # The size of the icon in it


class AssetWidget(QWidget):
    """
    Widget that displays each asset from the library in the interface.
    """

    def __init__(self, db_asset, in_controller, parent=None, width=100):
        QWidget.__init__(self, parent)
        self.db_asset = db_asset  # asset object from database
        self.Controller = in_controller
        self.width = width
        self.icon_path = Asset.dir_names(self.db_asset.path)["icon"]
        self.height = QPixmap(self.icon_path).scaledToWidth(self.width).height()

        if not self.height:
            self.height = self.width * 1.5

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.frame_image = QFrame()
        self.frame_image.setObjectName("frame_image")
        self.frame_image.setFixedSize(self.width, self.height)
        self.layout.addWidget(self.frame_image)
        self.frame_image.setStyleSheet("border-radius: 12px;"
                                       "background-color: #2c313c;"
                                       "border-image: url(" + self.icon_path + ") 0 0 0 0;")

        self.frame_shadow = QPushButton(parent=self)
        self.frame_shadow.setObjectName("frame_shadow")
        self.frame_shadow.setGeometry(0, 0, self.width, self.height)
        self.frame_shadow.installEventFilter(self)

        self.ast_label = QLabel(self.db_asset.name, parent=self.frame_shadow)
        self.ast_label.setToolTip(self.db_asset.name)
        self.ast_label.setGeometry(10, 10, self.width - 20, 22)
        self.ast_label.setStyleSheet("background-color: #16191d;"
                                     "border-radius: 10px;"
                                     "font: bold;"
                                     "padding: 0 10px;"
                                     "color: #fff;")

        self.open_button = QPushButton("", parent=self.frame_shadow)
        self.open_button.setGeometry(self.places_buttons_by_x()[0], self.height - 35, BTN_WIDTH, BTN_WIDTH)
        self.open_button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.open_button.setStyleSheet("background-color: #16191d;"
                                       "border-radius: " + str(BTN_WIDTH / 2) + "px;")

        self.edit_button = QPushButton("", parent=self.frame_shadow)
        self.edit_button.setGeometry(self.places_buttons_by_x()[1], self.height - 35, BTN_WIDTH, BTN_WIDTH)
        self.edit_button.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.edit_button.setStyleSheet("background-color: #16191d;"
                                       "border-radius: " + str(BTN_WIDTH / 2) + "px;")

        self.check_box = QPushButton("", parent=self.frame_shadow)
        self.check_box.setGeometry(self.places_buttons_by_x()[2], self.height - 35, BTN_WIDTH, BTN_WIDTH)
        self.check_box.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.check_box.setStyleSheet("background-color: #16191d;"
                                     "padding: 9px;"
                                     "border-radius: " + str(BTN_WIDTH / 2) + "px;")

        self.hidden_list = [self.ast_label, self.edit_button, self.check_box, self.open_button]

        if self.db_asset.path in self.Controller.ui.basket_list_widget.get_list():
            self.select_asset()
        else:
            self.deselect_asset()

        self.check_box.clicked.connect(self.check_box_state_changed)

        # if folder not exists
        if not os.path.exists(self.db_asset.path):
            self.frame_shadow.setText(" Asset missing")
            self.frame_image.setStyleSheet("border-radius: 12px;"
                                           "background-color: #b54444;"
                                           "border-image: none;")
        else:
            self.frame_shadow.clicked.connect(self.asset_overview)
            self.open_button.clicked.connect(self.open_directory)
            self.edit_button.clicked.connect(self.preparation_for_editing)

        if not os.path.exists(self.icon_path):
            self.frame_shadow.setIcon(QIcon(":/icons/icons/camera-off.svg"))
            self.frame_shadow.setIconSize(QtCore.QSize(25, 25))
            self.hidden_list.pop(0)  # liable not hiding
        self.outside_event()

        # connect Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_handler)

        # set font size
        size = self.Controller.ui.font_spinBox.value()
        set_font_size(self.ast_label, size)

        self.decorate_icons_color()

    def check_box_state_changed(self):
        if self.check_box.state:
            self.deselect_asset()
        else:
            self.select_asset()

    def select_asset(self):
        UiFunction.decorate_icon(self.check_box, "check-circle.svg")
        self.check_box.state = True
        if self.check_box in self.hidden_list:
            self.hidden_list.remove(self.check_box)
        self.Controller.ui.basket_list_widget.add_file(self.db_asset.path)

    def deselect_asset(self):
        UiFunction.decorate_icon(self.check_box, "circle.svg")
        self.check_box.state = False
        if self.check_box not in self.hidden_list:
            self.hidden_list.append(self.check_box)
        self.Controller.ui.basket_list_widget.remove_file(self.db_asset.path)

    def right_click_handler(self):
        menu = QMenu()
        menu.setStyleSheet("""background-color: #16191d; color: #fff; border-radius: 10px;""")
        menu.addAction(QAction("Delete asset", self))
        menu.addAction(QAction("Send to telegram", self))
        action = menu.exec_(QCursor().pos())
        if action:
            if action.text() == "Delete asset":
                self.delete_asset()
            if action.text() == "Send to telegram":
                send_message_to_bot(self.db_asset.name, self.icon_path, self.db_asset.path)

    def decorate_icons_color(self):
        """
        Adds a change in the color of the icons on the buttons when
        hovering over with the mouse
        """
        btn_dict = {self.open_button: "folder.svg",
                    self.edit_button: "edit.svg"
                    }
        for button in btn_dict:
            UiFunction.decorate_icon(button, btn_dict[button])

    def asset_overview(self):
        """
        starts the widget gallery view
        """
        self.Controller.ui.asset_menu_mode = "Add"
        logger.debug("\n\n__________________Asset " + self.db_asset.name + " clicked___________________")
        try:
            # open gallery page
            self.Controller.ui.drop_stackedWidget.setCurrentIndex(3)
            self.Controller.ui.decorate_buttons_background(3)
            if self.Controller.ui.drop_menu.width() == 0:
                self.Controller.ui.expand_close_animation("expand")
            self.Controller.ui.asset_overview_label.setText(" View asset " + self.db_asset.name)

            # get asset data
            asset_data = Asset.recognize_asset(self.db_asset.path, self.Controller.Models)

            # set description and form height
            self.Controller.ui.description_textEdit2.setPlainText(asset_data["description"])
            if not asset_data["description"]:
                self.Controller.ui.description_textEdit2.hide()
            else:
                self.Controller.ui.description_textEdit2.show()
                lines_num = len(asset_data["description"]) / 35
                self.Controller.ui.description_textEdit2.setFixedHeight(lines_num * 18 + 20)

            # clear old images from ui
            for i in range(self.Controller.ui.gallery_VLayout.count()):
                widget = self.Controller.ui.gallery_VLayout.itemAt(i).widget()
                if type(widget) == PyQt5.QtWidgets.QPushButton:
                    widget.deleteLater()

            # create new images if necessary
            asset_folders = Asset.dir_names(self.db_asset.path)
            preview_images = sorted(get_preview_images(**asset_folders), reverse=True)

            for icon_path, image_path in preview_images:
                image_preview_btn = QPushButton()
                image_preview_btn.clicked.connect(lambda y, x=image_path: self.open_image(x))
                pix = QPixmap(icon_path)
                pix = pix.scaledToWidth(DROP_MENU_WIDTH - 45, mode=Qt.SmoothTransformation)
                image_preview_btn.setFixedSize(pix.width(), pix.height())
                self.Controller.ui.gallery_VLayout.insertWidget(1, image_preview_btn)
                image_preview_btn.setStyleSheet("border-radius: 6px;"
                                                "background-color: #2c313c;"
                                                "border-image: url(" + icon_path + ") 0 0 0 0;}")

            logger.debug(self.db_asset.name + "\n")
            self.Controller.ui.status_message("")
        except Exception as message:
            logger.error(message)

    def open_image(self, path):
        """
        Opens a preview of the asset in the default Windows application
        """
        subprocess.call(path, shell=True)
        logger.debug(" Image opened" + "\n")

    def places_buttons_by_x(self, offset=0.05):
        """
        places three buttons on the x-axis
        """
        dist = COLUMN_WIDTH * offset
        widget_centre = COLUMN_WIDTH / 2
        return [widget_centre - BTN_WIDTH - BTN_WIDTH / 2 - dist,
                widget_centre - BTN_WIDTH / 2,
                widget_centre + BTN_WIDTH / 2 + dist]

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
        """
        Executed when the mouse is hovered over the asset
        """
        for elem in self.hidden_list:
            elem.show()
        self.frame_shadow.setStyleSheet("background-color: rgba(0, 0, 0, 100);"
                                        "border-radius: 12px;")

    def outside_event(self):
        """
        Executed when the mouse moves out of the bounds of the asset
        """
        self.frame_shadow.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        for elem in self.hidden_list:
            elem.hide()

    def open_directory(self):
        """
        open asset directory
        """
        subprocess.run(['explorer', os.path.realpath(self.db_asset.path)])

    def preparation_for_editing(self):
        """
        change the menu mode and fill in the fields for editing
        """
        self.Controller.ui.asset_menu_mode = "Edit"
        asset_data = Asset.recognize_asset(self.db_asset.path, self.Controller.Models)

        pattern = r"_ast$"
        asset_data['name'] = re.sub(pattern, "", asset_data['name'])

        self.Controller.ui.name_lineEdit.setText(asset_data['name'])

        self.Controller.ui.tag_flow_widget.clear()
        self.Controller.ui.tag_flow_widget.add_tags(asset_data['tags'])

        self.Controller.ui.path_lineEdit.setText(convert_path_to_local(asset_data['path']))
        self.Controller.ui.image_lineEdit.setText(asset_data['icon'])
        self.Controller.ui.description_textEdit.setPlainText(asset_data['description'])
        self.Controller.ui.file_list_widget.clear()
        self.Controller.ui.file_list_widget.add_files_list(asset_data['scenes'])
        self.Controller.ui.gallery_list_widget.clear()
        self.Controller.ui.gallery_list_widget.add_files_list(asset_data['gallery'])
        self.Controller.ui.current_asset = self.db_asset.id

        logger.debug("fill in the fields for editing")

    def delete_asset(self):
        """
        Opens a dialog box, then deletes the database entry and asset folder
        """
        try:
            dialog_message = "Delete asset", "Are you sure \nyou want to delete \nasset?"
            dialog = QMessageBox(QMessageBox.Critical, *dialog_message, parent=self.Controller.ui,
                                 buttons=QMessageBox.Ok | QMessageBox.Cancel)
            dialog.setStyleSheet("""background-color: #16191d; color: #fff;""")
            dialog_result = dialog.exec()
            if dialog_result == 1024:
                logger.debug("\n\n__________________Delete asset clicked___________________")

                process_result = self.Controller.Models.delete_asset(self.db_asset.name)
                self.Controller.get_from_folder(os.path.dirname(self.db_asset.path) + "/")

                if not process_result:
                    self.Controller.ui.status_message("information from the database was not deleted", state="ERROR")

                if not Asset.delete_asset(self.db_asset.name, self.db_asset.path):
                    self.Controller.ui.status_message("Information was removed only from database. "
                                                      "The asset folder may be in an undefined location.",
                                                      state="ERROR")
                logger.debug(" executed")
        except Exception as message:
            logger.error(message)
