# -*- coding: utf-8 -*-
import datetime
import json
import os
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from Utilities.Logging import logger
from Utilities.Utilities import get_library_path
from settings import INFO_FOLDER, CONTENT_FOLDER, GALLERY_FOLDER, SFX, ICON_WIDTH, DELETED_ASSET_FOLDER


class Asset:
    """
    The class defines an asset as a structure of folders and files.
    Contains methods for creating, modifying, and deleting assets
    """
    def __init__(self, in_controller, **kwargs):
        self.Controller = in_controller
        self.__icon = ""
        self.__path = None

        # folders for info and content
        self.asset_id = None
        self.asset_json = None
        self.asset_info_folder = None
        self.content_folder = None
        self.gallery_folder = None

        self.name = kwargs["name"]
        self.path = kwargs["path"]
        self.tags = kwargs.setdefault("tags", None)
        self.icon = kwargs.setdefault("icon", None)
        self.description = kwargs.setdefault("description", None)
        self.scenes = kwargs.setdefault("scenes", None)
        self.gallery = kwargs.setdefault("gallery", None)

        logger.debug(json.dumps(self.asset_data()))

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, in_path):
        self.__path = in_path
        self.asset_info_folder = in_path + "/" + INFO_FOLDER
        self.content_folder = in_path + "/" + CONTENT_FOLDER
        self.gallery_folder = in_path + "/" + GALLERY_FOLDER
        self.asset_json = self.asset_info_folder + "/data.txt"
        for each_path in [in_path, self.asset_info_folder, self.content_folder, self.gallery_folder]:
            if not os.path.exists(each_path):
                os.makedirs(each_path)

    @property
    def icon(self):
        return self.__icon

    @icon.setter
    def icon(self, new_path):
        # TODO: image format handler
        icon_default_path = self.asset_info_folder + "/icon.png"
        if new_path != icon_default_path:
            # delete the old path if there is no new path or if the new path is not equal to the old one
            if not new_path and os.path.exists(icon_default_path):
                try:
                    os.remove(icon_default_path)
                except Exception as message:
                    logger.error(message)
            if new_path:
                try:
                    icon = QPixmap(new_path).scaledToWidth(ICON_WIDTH, mode=Qt.SmoothTransformation)
                    icon.save(icon_default_path)

                    self.__icon = icon_default_path
                except Exception as message:
                    logger.error(message)
        else:
            self.__icon = icon_default_path

    def edit_asset(self):
        self.info_file(self.asset_json, self.asset_data())
        self.Controller.Models.edit_db_asset(**self.asset_data())

        self.verification_and_copying_files(self.scenes, self.content_folder)
        self.verification_and_copying_files(self.gallery, self.gallery_folder)

        self.Controller.refresh_ui()
        logger.debug("edit_asset")

    def verification_and_copying_files(self, source_files, destination_folder):
        destination_files = [destination_folder + "/" + x for x in os.listdir(destination_folder)]
        # if the file is not in the destination folder, copy it there
        while source_files:
            curent_file = source_files.pop()
            if curent_file in destination_files:
                destination_files.remove(curent_file)  # remove current_file from list destination_files
            else:
                file_name = os.path.basename(curent_file)
                shutil.copyfile(curent_file, destination_folder + "/" + file_name)
        # delete the remaining files in the destination folder
        for curent_file in destination_files:
            try:
                os.remove(curent_file)
            except Exception as message:
                logger.error(message)

    def create(self):
        if not self.Controller.Models.is_asset_in_db(self.name):
            logger.debug(" Start ")

            self.verification_and_copying_files(self.scenes, self.content_folder)
            self.verification_and_copying_files(self.gallery, self.gallery_folder)

            self.asset_id = self.Controller.Models.add_asset_to_db(**self.asset_data())
            self.info_file(self.asset_json, self.asset_data())
            if self.tags:
                self.Controller.ui.search_lineEdit.setText(self.tags[0])
            self.Controller.refresh_ui()
            self.Controller.ui.status_message("Asset " + self.name + " created successfully!", )
            logger.debug("executed")
        else:
            logger.error(" path : " + self.path + "/" + self.name + SFX + " exists")
            self.Controller.ui.status_message("Asset with " + self.name + " name already exists!", state="ERROR")

    @staticmethod
    def info_file(json_path, asset_data=None):  # if asset_data  create mode else read
        try:
            if asset_data:  # Create mode:
                with open(json_path, 'w') as outfile:
                    json.dump(asset_data, outfile, indent=4)
                logger.debug("Created json: " + json.dumps(asset_data))
                return True
            else:
                with open(json_path, "r") as read_file:
                    asset_data = json.load(read_file)
                    return asset_data
        except Exception as message:
            logger.error(message)

    @staticmethod
    def recognize_asset(path):
        """
        gets information about an existing asset, paths from info and files from folders
        """
        asset_json = path + "/" + INFO_FOLDER + "/data.txt"
        asset_data = Asset.info_file(asset_json)
        asset_content = os.listdir(asset_data["content_folder"])
        asset_data["scenes"] = [asset_data["content_folder"] + "/" + x for x in asset_content]
        gallery_content = os.listdir(asset_data["gallery_folder"])
        asset_data["gallery"] = [asset_data["gallery_folder"] + "/" + x for x in gallery_content]
        logger.debug(asset_data)
        return asset_data

    def delete_asset(self):
        process_result = self.Controller.Models.delete_asset(self.name)

        if not process_result:
            self.Controller.ui.status_message("information from the database was not deleted", state="ERROR")
        else:
            try:
                del_folder = get_library_path() + "/" + DELETED_ASSET_FOLDER
                if not os.path.exists(del_folder):
                    os.mkdir(del_folder)
                time = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
                os.rename(self.path, self.path + "_" + time)
                shutil.move(self.path + "_" + time, del_folder)
                logger.debug("Asset " + self.name + " deleted successfully")
                self.Controller.refresh_ui()
                self.Controller.ui.status_message("Asset " + self.name + " deleted successfully")
            except Exception as message:
                logger.error(message)
                self.Controller.ui.status_message("An error occurred and the asset was not correctly deleted",
                                                  state="ERROR")

    def asset_data(self):

        asset_data = dict()
        asset_data["name"] = self.name
        asset_data["path"] = self.path
        asset_data["asset_id"] = self.asset_id
        asset_data["icon"] = self.__icon
        asset_data["tags"] = self.tags
        asset_data["description"] = self.description
        asset_data["content_folder"] = self.content_folder
        asset_data["gallery_folder"] = self.gallery_folder
        asset_data["scenes"] = self.scenes
        asset_data["gallery"] = self.gallery

        return asset_data


if __name__ == '__main__':
    path = "U:/AssetStorage/library/food/fruit/orange2_ast/info/" + "icon.png"

    os.remove(path)

    # asset = Asset("hh")
    # data = asset.recognize_asset("U:/AssetStorage/library/weapon/shotgan_ast")
    # logger.debug("Created asset:  " + json.dumps(data, indent=4))
