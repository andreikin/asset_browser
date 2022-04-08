import os
import shutil
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QListView, QApplication, QAbstractItemView, QFileDialog
from Utilities.Logging import logger
from settings import CONTENT_FOLDER


class DeleteItemButton(QWidget):
    def __init__(self, in_item, in_widget, parent=None):
        super(DeleteItemButton, self).__init__(parent)
        self.in_widget = in_widget
        self.item = in_item
        layout = QHBoxLayout(self)

        self.button = QPushButton("")
        self.button.setIcon(QIcon(":/icons/icons//x-square.svg"))
        self.button.clicked.connect(self.btn_function)
        self.button.setFixedSize(self.in_widget.item_height, self.in_widget.item_height, )
        layout.addWidget(self.button, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 5, 0)

    def btn_function(self):
        try:
            path = self.item.data(role=Qt.ToolTipRole)
            logger.debug(path)
            self.in_widget.model.removeRow(self.item.row())
            self.in_widget.set_height()

            # only for basket widget deselect function
            if self.in_widget.update_gallery:
                self.in_widget.deselect_asset_in_gallery(path)

        except Exception as message:
            logger.error(message)


class FileListWidget(QListView):
    """
    class creates a list of files with a button to delete each of them
    """

    def __init__(self, in_controller, files_list, parent=None):
        super(FileListWidget, self).__init__(parent=parent)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.item_height = 22
        self.min_height = self.item_height * 2
        self.model = QStandardItemModel(self)

        self.setModel(self.model)
        self.setStyleSheet("QListView {padding: 10px 10px 2px 20px;"
                           "border-radius: 5px;"
                           "background-color:#1f232a;}"
                           "QListView:item {"
                           "color:#fff;"
                           "height: " + str(self.item_height) + "px;}")
        if files_list:
            self.add_files_list(files_list)
        self.set_height()

        # for basket widget: if del item --> uncheck asset widget
        self.update_gallery = False
        self.Controller = in_controller

    def remove_file(self, file_path):
        try:
            for index in range(self.model.rowCount()):
                item = self.model.item(index)
                path = item.data(role=Qt.ToolTipRole)
                if file_path == path:
                    self.model.removeRow(item.row())
                    self.set_height()
        except Exception as message:
            logger.error(message)

    def create_item(self, file_path):
        try:
            if not self.is_file_in_widget(file_path):
                file_name = os.path.basename(file_path)
                label = file_name if len(file_name) < 30 else file_name[:29] + "..."
                item = QStandardItem(label)
                item.setData(file_path, role=Qt.ToolTipRole)
                self.model.appendRow(item)
                self.setIndexWidget(item.index(), DeleteItemButton(item, self))
                self.set_height()
                logger.debug("File added to ui " + file_path)
        except Exception as message:
            logger.error(message)

    def is_file_in_widget(self, file):
        return file in self.get_list()

    def add_file(self, file_path):
        self.create_item(file_path)

    def add_files_list(self, files_list):
        for file_path in files_list:
            self.create_item(file_path)

    def get_list(self):
        path_list = []
        for index in range(self.model.rowCount()):
            item = self.model.item(index)
            path_list.append(item.data(role=Qt.ToolTipRole))
        return path_list

    def set_height(self):
        """
        sets the height of the widget according to the amount of content
        """
        files_list = self.get_list()
        content_height = len(files_list) * self.item_height
        if self.min_height < content_height + 20:
            self.setFixedHeight(content_height + 20)
        else:
            self.setFixedHeight(self.min_height + 20)

    def clear(self):
        self.model.clear()
        self.set_height()

    def dropEvent(self, event):
        mimedata = event.mimeData()
        if mimedata.hasUrls():
            for f in mimedata.urls():
                self.add_file(f.path()[1:])

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
        if event.source() is self:
            event.ignore()
        else:
            mimedata = event.mimeData()
            if mimedata.hasUrls():
                event.accept()
            else:
                event.ignore()


class BasketWidget(FileListWidget):
    """
    class creates a list of files with a button to delete each of them
    """
    def __init__(self, in_controller, files_list=None, parent=None):
        super(BasketWidget, self).__init__(in_controller, files_list, parent=parent)
        if files_list is None:
            files_list = []

    def export_assets(self):
        try:
            logger.debug("\n__________________Export assets button clicked___________________")
            path_list = self.get_list()
            target_folder = QFileDialog.getExistingDirectory(self, directory=self.Controller.lib_path)
            target_folder = target_folder.replace("\\", "/")

            if target_folder and path_list:
                copy_list = []
                for path in path_list:
                    folder = os.path.basename(path)
                    srs_files = os.listdir(path + "/" + CONTENT_FOLDER)
                    for file in srs_files:
                        srs = path + "/" + CONTENT_FOLDER + "/" + file
                        dst = target_folder + "/" + folder + "/" + file
                        copy_list.append([srs, dst])

                self.Controller.ui.add_task(lambda: self.export_files(copy_list))

            for path in path_list:
                self.deselect_asset_in_gallery(path)

            logger.debug(" executed")
        except Exception as message:
            logger.error(message)

    def export_files(self, copy_list):
        self.Controller.ui.copy_progress_bar.hide()
        for source_files, destination_files in copy_list:
            self.Controller.ui.copy_function.copy(source_files, destination_files)
        self.Controller.ui.copy_progress_bar.hide()

    def deselect_asset_in_gallery(self, path):
        for asset in self.Controller.ui.gallery.vidget_list:
            if path == asset.db_asset.path:
                asset.deselect_asset()
                asset.outside_event()


if __name__ == '__main__':
    target_folder = "C:/Users/avbeliaev/Desktop/tmp/assss111_ast"
    asset = "U:/AssetStorage/library/characters/girl04_ast"

