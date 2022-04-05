# -*- coding: utf-8 -*-
import os
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from Utilities.Utilities import copy_file

if __name__ == '__main__':
    from Logging import logger
else:
    from Utilities.Logging import logger
from settings import IMAGE_PREVIEW_SUFFIX, SFX, DROP_MENU_WIDTH


class CopyInThread(QtCore.QThread):
    """
    Class that copies the list of assets to the selected folder
    """

    def __init__(self, parent=None, **kwargs):
        QtCore.QThread.__init__(self, parent)
        self.copy_list = kwargs.setdefault("copy_list", None)
        self.progress_bar = kwargs.setdefault("progress_bar", None)

    def run(self):
        try:
            self.progress_bar.show()
            for source_files, destination_files in self.copy_list:
                copy_file(source_files, destination_files, progress_bar=self.progress_bar)
            self.progress_bar.hide()
        except Exception as message:
            logger.error(message)


class CreateAssetThread(QtCore.QThread):
    """
    The thread that manages copying files and creating preview images
    """

    def __init__(self, parent=None, **kwargs):
        QtCore.QThread.__init__(self, parent)
        logger.debug(" started")

        self.copy_list = []
        self.name = kwargs.setdefault("name", None)
        self.path = kwargs.setdefault("path", None)
        self.scenes = kwargs.setdefault("scenes", None)
        self.gallery = kwargs.setdefault("gallery", None)
        self.asset_info_folder = kwargs.setdefault("info_folder", None)
        self.content_folder = kwargs.setdefault("content_folder", None)
        self.gallery_folder = kwargs.setdefault("gallery_folder", None)
        self.rename_content = kwargs.setdefault("rename_content", None)
        self.progress_bar = kwargs.setdefault("progress_bar", None)

    def run(self):
        try:
            self.progress_bar.show()
            for source_files, destination_files in self.copy_list:
                copy_file(source_files, destination_files, progress_bar=self.progress_bar)
            self.create_preview_images()
            self.rename_scenes()
            self.progress_bar.hide()
            logger.debug(" executed  ")
        except Exception as message:
            logger.error(message)

    def create_preview_images(self):
        try:
            if os.path.exists(self.gallery_folder):
                # get gallery content
                gallery_content = os.listdir(self.gallery_folder)
                for file in gallery_content:
                    filename, file_extension = os.path.splitext(file)
                    icon_path = self.asset_info_folder + "/" + filename + IMAGE_PREVIEW_SUFFIX + file_extension
                    image_path = self.gallery_folder + "/" + filename + file_extension
                    if not os.path.exists(icon_path):
                        image_light = QPixmap(self.gallery_folder + "/" + file)
                        image_light = image_light.scaledToWidth(DROP_MENU_WIDTH - 45,
                                                                mode=QtCore.Qt.SmoothTransformation)
                        image_light.save(icon_path)
        except Exception as message:
            logger.error(message)

    def rename_scenes(self):
        try:
            if self.rename_content:
                scenes_list = os.listdir(self.content_folder)
                numbers = {os.path.splitext(x)[-1]: 0 for x in scenes_list}
                name = self.name + SFX
                self.content_folder += "/"
                for ext in numbers:
                    files = [x for x in scenes_list if ext == os.path.splitext(x)[-1]]
                    if len(files) == 1:
                        os.rename(self.content_folder + files[0], self.content_folder + name + ext)
                    else:
                        i = 1
                        for file in files:
                            num = '_v{0:02d}'.format(i)
                            os.rename(self.content_folder + file, self.content_folder + name + num + ext)
                            i += 1
        except Exception as message:
            logger.error(message)
