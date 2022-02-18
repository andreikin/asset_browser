import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QSizeGrip


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.offset = None
        self.setWindowFlags(Qt.FramelessWindowHint)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CustomTitleBar()
    window.show()
    window.resize(240, 160)
    app.exec_()