import os
import tempfile

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QLineEdit, QApplication, QMenu, QAction


class IconLineEdit(QLineEdit):    # image_lineEdit
    def __init__(self, parent=None):
        super(IconLineEdit, self).__init__(parent)
        # add contrext menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.icon_line_edit_context_menu)

        self.setPlaceholderText("Add path to icon here")
        self.setClearButtonEnabled(True)
        self.setDragEnabled(True)
        self.setMinimumHeight(22)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            # for some reason, this doubles up the intro slash
            filepath = str(urls[0].path())[1:]
            self.setText(filepath)

    def icon_line_edit_context_menu(self):
        """
        creates a context menu that allows you to insert an image from a clipboard
        """
        menu = QMenu()
        menu.setStyleSheet("""background-color: #16191d; color: #fff;""")
        menu.addAction(QAction("Paste from clipboard", self))
        action = menu.exec_(QCursor().pos())
        if action and action.text() == "Paste from clipboard":
            clipboard = QApplication.clipboard()
            icon = clipboard.image()
            if icon:
                file_path = os.path.join(tempfile.gettempdir(), 'tmp_image.png')
                result = icon.save(file_path)
                if result:
                    file_path = file_path.replace("\\", "/")
                    self.setText(file_path)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = IconLineEdit()
    window.resize(200, 24)
    window.show()
    sys.exit(app.exec_())