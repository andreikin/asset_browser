from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtWidgets import (QApplication, QLayout, QPushButton, QSizePolicy,
                             QWidget, QVBoxLayout, QLabel)

from UI.Ui_function import UiFunction


class FlowLayout(QLayout):
    """
    Layout that arranges components line by line horizontally.
    """
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margin, _, _, _ = self.getContentsMargins()

        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton,
                                                                Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton,
                                                                Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


class TagLabel(QLabel):
    """
    Tag widget with delete button
    """
    def __init__(self, tag, parent=None):
        QLabel.__init__(self, parent)
        self.tag = tag
        self.items_list = None

        self.setText(self.tag)
        width = self.sizeHint().width()
        self.setFixedSize(width + 35, 24)
        self.setStyleSheet("background-color: #1f232a;"
                           "border-radius: 11px;"
                           "padding: 2 6px;"
                           "color: #fff;")

        button = QPushButton("", parent=self)
        button.setFixedSize(15, 15)
        button.setGeometry(width + 15, 4, -20, 20)
        UiFunction.decorate_icon(button, "x-circle.svg")
        button.clicked.connect(self.delete)

    def delete(self):
        for item in self.items_list:
            if item.tag == self.tag:
                self.items_list.remove(item)

        print([x.tag for x in self.items_list])
        self.deleteLater()


class TagFlowWidget(QWidget):
    """
    Creates a set of tags with a delete button.
    Has the functions of clearing and getting a list of tags
    """
    def __init__(self):
        QWidget.__init__(self)
        self.items_list = []
        self.layout = FlowLayout()
        self.setLayout(self.layout)

    def add_tags(self, tags):
        for tag in tags:
            if tag not in self.tags():
                item = TagLabel(tag)
                self.layout.addWidget(item)
                self.items_list.append(item)
                item.items_list = self.items_list

    def clear(self):
        for item in self.items_list:
            item.deleteLater()
        self.items_list = []

    def tags(self):
        return [x.tag for x in self.items_list]




if __name__ == '__main__':
    import sys
    class Window(QWidget):
        def __init__(self):
            super(Window, self).__init__()
            labels = "This attribute controls how the joint is drawn bone setting draws the joints as normal".split()
            laut = QVBoxLayout()
            self.setLayout(laut)

            self.flow_widget = TagFlowWidget()
            self.flow_widget.add_tags(labels)
            laut.addWidget(self.flow_widget)

            bt = QPushButton("clear")
            laut.addWidget(bt)
            bt.clicked.connect(self.cl)

        def cl(self):
            print(self.flow_widget.tags())

    app = QApplication(sys.argv)
    mainWin = Window()
    mainWin.show()
    sys.exit(app.exec_())
