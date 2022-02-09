import os
import re
import subprocess
import sys

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QApplication, QScrollArea, QTreeWidget, QTreeWidgetItem, QVBoxLayout, \
    QPushButton, QInputDialog, QDialog, QMenu, QAction

from Utilities.Logging import logger
from Utilities.Utilities import convert_path_to_local
from settings import DELETED_ASSET_FOLDER


class BaseTreeWidget(QTreeWidget):
    def __init__(self, in_controller, parent=None, ):
        QTreeWidget.__init__(self, parent)

        self.Controller = in_controller
        self.path = in_controller.lib_path
        self.setHeaderHidden(True)

        if self.Controller.connect_db:
            self.update_ui()

        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.setStyleSheet("QTreeView {\n"
                           "border-radius: 10px;}\n"
                           "QTreeWidget::item{ height:20px;"
                           "margin: 0px 0px 4px 0px;} ")
        logger.debug(" executed")

    def get_tree(self, parent=None, root=None):
        if not parent:
            parent = self.invisibleRootItem()
        if not root:
            root = self.path
        for f in os.listdir(root):
            filepath = os.path.join(root, f)
            pattern = r"_ast$"
            if os.path.isdir(filepath) and not re.search(pattern, filepath) and not re.search(DELETED_ASSET_FOLDER, filepath):
                item = QTreeWidgetItem()
                parent.addChild(item)
                item.setText(0, f)
                item.setData(0, 32, filepath)
                self.get_tree(item, filepath)

    def update_ui(self):
        self.clear()
        self.path = self.Controller.lib_path
        if self.Controller.lib_path:
            self.get_tree()
            self.expandAll()

    def add_directory(self):
        if self.Controller.ui.add_dir_line_edit.text():
            dir_name = self.Controller.ui.add_dir_line_edit.text()
            """ if item not select"""
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


class MenuTreeWidget(BaseTreeWidget):
    def __init__(self, in_controller, parent=None):
        BaseTreeWidget.__init__(self, in_controller, parent)
        self.itemDoubleClicked.connect(self.double_click_handler)
        # connect Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_handler)

    def double_click_handler(self, item):
        self.Controller.ui.search_lineEdit.setText(item.data(0, 0))
        self.Controller.refresh_ui()

    def right_click_handler(self, pos):
        menu = QMenu()
        menu.setStyleSheet("""background-color: #16191d; color: #fff;""")

        menu.addAction(QAction("Open in explorer", self))
        menu.addAction(QAction("Add asset", self))
        action = menu.exec_(QCursor().pos())
        path = self.selectedItems()[0].data(0, 32).replace("\\", "/")+"/"
        if action:
            if action.text() == "Open in explorer":
                subprocess.run(['explorer', os.path.realpath(path)])
            if action.text() == "Add asset":
                self.Controller.ui.switch_pages(0)
                self.Controller.ui.clear_form()
                self.Controller.ui.path_lineEdit.setText(convert_path_to_local(path))


if __name__ == '__main__':
    class Controller():
        def __init__(self, in_path):
            self.lib_path = in_path


    class SimpleWindow(QWidget):
        def __init__(self):
            super(SimpleWindow, self).__init__()
            ly = QVBoxLayout()

            controller = Controller("U:\AssetStorage\library")

            self.tree_widget = MenuTreeWidget(controller)
            ly.addWidget(self.tree_widget)
            btn = QPushButton("add")

            btn.clicked.connect(self.tree_widget.add_directory)

            ly.addWidget(btn)

            self.setLayout(ly)
            self.resize(500, 400)


    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()

    app.exec_()
