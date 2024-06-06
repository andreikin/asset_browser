# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFrame, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget, \
    QScrollArea

from UI.AssetWidget import AssetWidget
from UI.TagFlowWidget import FlowLayout
from Utilities.Logging import logger
from settings import SPACING, COLUMN_WIDTH


class GalleryWidget(QWidget):
    """
    widget displaying child widgets as a pinterest gallery
    """
    scroll_bar_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None, icons_width=50, spacing=SPACING, mine_window=None):
        QWidget.__init__(self, parent)

        self.widget_list = []
        self.icons_width = icons_width
        self.mine_window = mine_window
        self.spacing = spacing
        self.gallery_old_size = None

        self.setMinimumWidth(self.icons_width+30)

        self.layout = QHBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.layout)

        self.background = QFrame()
        self.background_layout = QHBoxLayout(self.background)

        self.flow_layout = FlowLayout(spacing=self.spacing)
        self.background_layout.addLayout(self.flow_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.background)
        self.layout.addWidget(self.scroll_area)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.scroll_bar = self.scroll_area.verticalScrollBar()
        self.scroll_bar.valueChanged.connect(self.scroll_bar_handler)

    def set_size(self):
        resolution_factor = self.mine_window.resolution_factor if self.mine_window else 1
        for widget in self.widget_list:
            widget.set_size(resolution_factor)

    def add_assets(self, number_to_add=10):
        """
        Staged loading of assets function
        """

        try:
            found_assets_num = len(self.mine_window.Controller.found_assets)
            widget_num = len(self.widget_list)
            for i in range(widget_num, widget_num+number_to_add):
                if len(self.widget_list)<found_assets_num:
                    asset = self.mine_window.Controller.found_assets[i]
                    asset_widget = AssetWidget(asset, self.mine_window.Controller)
                    self.add_widget(asset_widget)

        except Exception as message:
            logger.error(message)

    def resizeEvent(self, event):
        """
        When changing the widget size, adds more asset buttons if necessary
        """
        super().resizeEvent(event)
        cur_asset_num = len(self.widget_list)

        width = int(COLUMN_WIDTH * self.mine_window.resolution_factor)
        des_assets_in_row = self.size().width()//(self.spacing + width)
        des_assets_in_col = self.size().height() // (self.spacing + int(width * 1.5))+1

        if des_assets_in_row*des_assets_in_col > cur_asset_num:
            self.add_assets(des_assets_in_row*des_assets_in_col-cur_asset_num)

    def scroll_bar_handler(self):
        """
        Starts the asset loading function
        """
        try:
            if (self.scroll_bar.maximum() - 150) < self.scroll_bar.value():
                self.add_assets()
        except Exception as message:
            print(message)

    def add_widget(self, widget):
        self.flow_layout.addWidget(widget)
        self.widget_list.append(widget)

    def clear(self):
        for i in range(self.flow_layout.count()):
            self.flow_layout.itemAt(i).widget().deleteLater()
        self.widget_list = []


if __name__ == "__main__":
    pass
    # import sys

    #
    # class MyWindow(QWidget):
    #     def __init__(self, parent=None):
    #         QWidget.__init__(self, parent)
    #         self.vbox = QVBoxLayout()
    #         self.gallery = GalleryWidget(icons_width=100, spacing=8)
    #         self.vbox.addWidget(self.gallery)
    #         for x in range(135):
    #             but = QPushButton()
    #             but.setFixedSize(140, 210)
    #             self.gallery.add_widget(but)
    #         style_sheet = """
    #                    QPushButton {
    #                        border-radius: 4px;
    #                        background-color: rgb(100, 100, 100); }
    #                    """
    #         self.setStyleSheet(style_sheet)
    #         self.setLayout(self.vbox)
    #
    #
    # app = QApplication(sys.argv)
    # window = MyWindow()
    # window.resize(1000, 600)
    # window.show()
    # sys.exit(app.exec_())
