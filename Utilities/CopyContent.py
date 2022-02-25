# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtTest import QTest

from Asset import Asset
from Utilities.Logging import logger


class MyThread(QtCore.QThread):
    end_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, **kwargs):
        QtCore.QThread.__init__(self, parent)
        self.name = kwargs["name"]
        self.path = kwargs["path"]

        self.scenes = kwargs.setdefault("scenes", None)
        self.gallery = kwargs.setdefault("gallery", None)
        self.asset_info_folder = Asset.dir_names(self.path)["info_folder"]
        self.content_folder = Asset.dir_names(self.path)["content_folder"]
        self.gallery_folder = Asset.dir_names(self.path)["gallery_folder"]
        self.rename_content = kwargs.setdefault("rename_content", None)

    def run(self):
        for i in range(1, 10):
            logger.debug(" executed" + str(i))
            QTest.qWait(1000)
        # Передача данных из потока через сигнал

        self.end_signal.emit("test")
