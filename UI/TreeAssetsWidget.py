import os
import re
import shutil
import subprocess

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction, QInputDialog, QMessageBox, QAbstractItemView

from Asset import Asset
from Utilities.Logging import logger
from Utilities.Utilities import convert_path_to_local
from settings import DELETED_ASSET_FOLDER, CLIENT_MODE


class MenuTreeWidget(QTreeWidget):
    def __init__(self, in_controller, parent=None, ):
        QTreeWidget.__init__(self, parent)
        self.setDragDropMode(QAbstractItemView.DropOnly)

        # enabling the ability to deselect an item
        self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)

        self.Controller = in_controller
        self.path = in_controller.lib_path
        self.items_list = []
        self.setHeaderHidden(True)

        if self.Controller.connect_db:
            self.update_ui()

        self.setItemsExpandable(True)
        self.setExpandsOnDoubleClick(False)
        self.setRootIsDecorated(False)
        self.setStyleSheet("""
            QTreeView::branch:has-siblings:!adjoins-item {
                border-image: url(:/icons/icons/vline.png) 0;
            }

            QTreeView::branch:has-siblings:adjoins-item {
                border-image: url(:/icons/icons/branch-more.png) 0;
            }

            QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                border-image: url(:/icons/icons/branch-end.png) 0;
            }

            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                    border-image: none;
                    image: url(:/icons/icons/branch-closed.png);
            }

            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings  {
                    border-image: none;
                    image: url(:/icons/icons/branch-open.png);
            }
        """)

        self.itemDoubleClicked.connect(self.double_click_handler)
        # connect Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        if not CLIENT_MODE:
            self.customContextMenuRequested.connect(self.right_click_handler)
        logger.debug(" executed")

    def get_settings(self, settings):
        for item in self.items_list:
            if item.data(0, 32) in settings:
                val = settings[item.data(0, 32)]
                item.setExpanded(val)

    def save_setting(self):
        settings = dict()
        for i in self.items_list:
            settings[i.data(0, 32)] = i.isExpanded()
        return settings

    def get_tree(self, parent=None, root=None):
        if not parent:
            parent = self.invisibleRootItem()
        if not root:
            root = self.path
        for f in os.listdir(root):
            filepath = "/".join([root, f])
            pattern = r"_ast$"
            if os.path.isdir(filepath) and not re.search(pattern, filepath) \
                    and not re.search(DELETED_ASSET_FOLDER, filepath):
                item = QTreeWidgetItem()
                self.items_list.append(item)
                parent.addChild(item)
                item.setText(0, f)
                item.setData(0, 32, filepath)
                if root == self.path:
                    item.setExpanded(True)
                self.get_tree(item, filepath)

    def update_ui(self):
        try:
            self.clear()
            self.path = self.Controller.lib_path
            if self.Controller.lib_path:
                self.get_tree()
        except Exception as message:
            logger.error(message)

    def add_directory(self):
        dir_name = None
        if self.Controller.ui.add_dir_line_edit.text():
            dir_name = self.Controller.ui.add_dir_line_edit.text()
        else:
            # folder name dialog
            dialog = QInputDialog(self)
            dialog.setLabelText("Add folder :")
            dialog.setOkButtonText("   Add  ")
            dialog.setCancelButtonText("   Cancel  ")
            dialog.setInputMode(QInputDialog.TextInput)
            dialog_result = dialog.exec()
            if dialog_result == 1 and dialog.textValue():
                dir_name = dialog.textValue()
        if dir_name:
            # if item not select
            if not self.selectedItems():
                path = os.path.abspath(self.Controller.lib_path + "/" + dir_name)
            else:
                path = self.selectedItems()[0].data(0, 32)
                path = os.path.abspath(path + "/" + dir_name)
            os.mkdir(path)
            self.update_ui()
            self.Controller.ui.add_dir_line_edit.setText("")
        else:
            self.Controller.ui.status_message("You must enter a directory name")

    def double_click_handler(self, item):
        logger.debug("\n\n__________________Find asset in folder clicked___________________")
        path = item.data(0, 32) + "/"
        self.Controller.ui.search_lineEdit.setText(item.data(0, 0).lower())
        self.Controller.get_from_folder(path)

    def right_click_handler(self, pos):
        menu = QMenu()
        menu.setStyleSheet("""background-color: #16191d; color: #fff;""")
        menu.addAction(QAction("Open in explorer", self))
        menu.addAction(QAction("Add asset", self))
        menu.addAction(QAction("Add folder", self))
        menu.addAction(QAction("Rename folder", self))
        menu.addAction(QAction("Delete folder", self))
        action = menu.exec_(QCursor().pos())
        try:
            path, name = None, None
            if self.selectedItems():
                path = self.selectedItems()[0].data(0, 32) + "/"
                name = self.selectedItems()[0].data(0, 0)
            if action:
                if action.text() == "Open in explorer":
                    subprocess.run(['explorer', os.path.realpath(path)])
                if action.text() == "Add asset":
                    self.Controller.ui.switch_pages(0)
                    self.Controller.ui.asset_menu_mode = "Add"
                    self.Controller.ui.clear_form()
                    self.Controller.ui.path_lineEdit.setText(convert_path_to_local(path))
                if action.text() == "Rename folder":
                    self.rename_path(path)
                if action.text() == "Delete folder":
                    self.delete_folder(name, path)
                if action.text() == "Add folder":
                    self.add_directory()

        except Exception as message:
            logger.error(message)

    def delete_folder(self, name, path):
        """
        Deletes all assets inside the folder and then the folder itself
        """
        try:
            dialog_message = "Delete asset", "Are you sure \nyou want to delete \nfolder?"
            dialog = QMessageBox(QMessageBox.Critical, *dialog_message, parent=self.Controller.ui,
                                 buttons=QMessageBox.Ok | QMessageBox.Cancel)
            dialog.setStyleSheet("""background-color: #16191d; color: #fff;""")
            dialog_result = dialog.exec()
            logger.debug("\n\n__________________Delete folder clicked___________________")
            if dialog_result == 1024:

                db_assets = self.Controller.Models.get_all_from_folder(path)
                if db_assets:
                    for asset in db_assets:
                        self.Controller.Models.delete_asset(asset.name)
                Asset.delete_asset(name, path)
                self.Controller.ui.gallery.clear()
                self.update_ui()

        except Exception as message:
            logger.error(message)

    def rename_path(self, path):
        """
        Renames the folder and changes all asset paths inside
        """
        dialog = QInputDialog(self)
        dialog.setLabelText("Rename folder :")
        dialog.setOkButtonText("   Rename  ")
        dialog.setCancelButtonText("   Cancel  ")
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setTextValue(self.selectedItems()[0].data(0, 0))
        dialog_result = dialog.exec()

        if dialog_result == 1 and dialog.textValue():
            old_name = self.selectedItems()[0].data(0, 0)
            new_name = dialog.textValue()
            new_path = path[:-len(old_name) - 1] + new_name + "/"
            # edit db
            self.Controller.Models.rename_directory(path, new_path, old_name, new_name)
            os.rename(path, new_path)

            self.selectedItems()[0].setText(0, new_name)
            self.selectedItems()[0].setData(0, 32, new_path)

    def replace_asset(self, srs, dst):
        """
        Function moves the specified asset to another directory
        """
        try:
            name = os.path.basename(srs)
            args = self.Controller.Models.find_asset(path=srs)
            keys = ("asset_id", "name", "path")
            kwargs = dict(zip(keys, args))
            kwargs["path"] = dst + "/" + name
            self.Controller.Models.edit_db_asset(**kwargs)
            if not os.path.exists(dst + "/" + name):
                shutil.move(srs, dst + "/" + name)

            for i in range(len(self.Controller.ui.gallery.widget_list)):
                asset_widget = self.Controller.ui.gallery.widget_list[i]
                if asset_widget.ast_label.text() == kwargs["name"]:
                    asset_widget.deleteLater()
                    self.Controller.ui.gallery.widget_list.pop(i)
        except Exception as message:
            logger.error(message)

    def dropEvent(self, event):
        to_index = self.indexAt(event.pos())
        dst = to_index.data(32) if to_index.isValid() else None
        mimedata = event.mimeData()
        if mimedata.hasUrls() and dst:
            for f in mimedata.urls():
                self.replace_asset(f.path()[1:], dst)
        self.colorize_items()

    def dragEnterEvent(self, event):
        if event.source() is self:
            event.ignore()
        else:
            mimedata = event.mimeData()
            if mimedata.hasUrls():
                event.accept()
            else:
                event.ignore()

    def dragMoveEvent(self, event):
        try:
            if event.source() is self:
                event.ignore()
            else:
                mimedata = event.mimeData()
                if mimedata.hasUrls():
                    event.accept()
                    self.colorize_items()
                    item = self.itemAt(event.pos())
                    item.setBackground(0, QColor("#16191d"))
                else:
                    event.ignore()
        except Exception as message:
            logger.error(message)

    def dragLeaveEvent(self, event):
        self.colorize_items()

    def colorize_items(self, root=None):
        """
        Paint all elements except the one over which the mouse pointer
        """
        if not root:
            root = self.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            item.setBackground(0, QColor("#1f232a"))
            if item.childCount():
                self.colorize_items(root=item)
