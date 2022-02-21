# -*- coding: utf-8 -*-
import datetime
import json
import os
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from Utilities.Logging import logger
from Utilities.Utilities import get_library_path, get_preview_images, rename_path_list
from settings import INFO_FOLDER, CONTENT_FOLDER, GALLERY_FOLDER, ICON_WIDTH, DELETED_ASSET_FOLDER, SFX


class Asset:
    """
    The class defines an asset as a structure of folders and files.
    Contains methods for creating, modifying, and deleting assets
    """

    def __init__(self, in_controller, **kwargs):
        try:
            self.Controller = in_controller

            self.name = kwargs["name"]
            self.path = kwargs["path"]
            self.asset_id = kwargs.setdefault("asset_id", None)
            self.tags = kwargs.setdefault("tags", None)
            self.icon = kwargs.setdefault("icon", None)
            self.scenes = kwargs.setdefault("scenes", None)
            self.gallery = kwargs.setdefault("gallery", None)
            self.description = kwargs.setdefault("description", None)

            self.asset_info_folder = Asset.dir_names(self.path)["info_folder"]
            self.content_folder = Asset.dir_names(self.path)["content_folder"]
            self.gallery_folder = Asset.dir_names(self.path)["gallery_folder"]
            self.asset_json = Asset.dir_names(self.path)["asset_json"]

            # if old asset data exist set edit mod
            self.old_asset_data = self.get_old_asset_data() if self.asset_id else None

            logger.debug(json.dumps(self.asset_data()))

        except Exception as message:
            logger.error(message)

    def create(self):
        if not self.Controller.Models.find_asset(name=self.name):

            # mack folders
            for each_path in [self.path, self.asset_info_folder, self.content_folder, self.gallery_folder]:
                if not os.path.exists(each_path):
                    os.makedirs(each_path)

            # set asset icon
            self.icon = self.create_icon("icon.png", self.icon, ICON_WIDTH)

            # add to database and record info file
            self.asset_id = self.Controller.Models.add_asset_to_db(**self.asset_data())
            self.write_info_file(self.asset_json, self.asset_data())

            # copy files
            self.copy_files()
            self.Controller.refresh_ui()
            logger.debug(" executed")
        else:
            logger.error(" path : " + self.path + " exists")
            self.Controller.ui.status_message("Asset with " + self.name + " name already exists!", state="ERROR")

    def create_icon(self, name, seurce, width):
        if seurce:
            icon = QPixmap(seurce).scaledToWidth(width, mode=Qt.SmoothTransformation)
            asset_icon_path = self.path + "/" + INFO_FOLDER + "/" + name
            icon.save(asset_icon_path)
            return asset_icon_path

    def edit(self):
        self.edit_name()
        self.edit_path()
        self.edit_icon()

        self.write_info_file(self.asset_json, self.asset_data())
        self.Controller.Models.edit_db_asset(**self.asset_data())

        # copy files
        self.copy_files()

        self.Controller.refresh_ui()
        logger.debug(" executed")

    def edit_path(self):
        if self.path != self.old_asset_data["path"]:
            try:
                shutil.move(self.old_asset_data["path"], self.path)
                for i in range(len(self.gallery)):
                    self.gallery[i] = self.gallery[i].replace(self.old_asset_data["path"], self.path)
                for i in range(len(self.scenes)):
                    self.scenes[i] = self.scenes[i].replace(self.old_asset_data["path"], self.path)
            except Exception as message:
                logger.error(message)

    def edit_name(self):
        if self.name != self.old_asset_data["name"]:
            try:
                # rename folders
                new_asset_path = rename_path_list(self.old_asset_data["name"], self.name, [self.old_asset_data["path"]])[0]
                self.scenes = rename_path_list(self.old_asset_data["name"], self.name, self.scenes)
                self.gallery = rename_path_list(self.old_asset_data["name"], self.name, self.gallery)
                os.rename(self.old_asset_data["path"], new_asset_path)
                self.old_asset_data["path"] = new_asset_path
                # bd path edit
                self.Controller.Models.edit_db_asset(**{"name": self.name,
                                                        "asset_id": self.old_asset_data["asset_id"],
                                                        "path": new_asset_path})
                # edit info
                asset_json = self.dir_names(new_asset_path)["asset_json"]
                asset_data = self.info_file(asset_json)
                asset_data["name"] = self.name
                self.write_info_file(asset_json, asset_data)

                logger.debug(" executed")
            except Exception as message:
                logger.error(message)
                return None

    def edit_icon(self):
        icon_default_path = Asset.dir_names(self.path)["icon"]
        if self.icon != icon_default_path:
            # delete the old path if there is no new path or if the new path is not equal to the old one
            if not self.icon and os.path.exists(icon_default_path):
                os.remove(icon_default_path)
            if self.icon:
                self.icon = self.create_icon("icon.png", self.icon, ICON_WIDTH)


    def get_old_asset_data(self):
        out = dict()
        try:
            out["asset_id"], out["name"], out["path"] = self.Controller.Models.find_asset(id=self.asset_id)
            logger.debug(" executed")
        except Exception as message:
            logger.error(message)
        return out


    def copy_files(self):
        try:
            for source_files, destination_folder in [(self.scenes, self.content_folder),
                                                     (self.gallery, self.gallery_folder)]:
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
                    os.remove(curent_file)
            asset_folders = Asset.dir_names(self.path)
            get_preview_images(**asset_folders)
        except Exception as message:
            logger.error(message)


    @staticmethod
    def info_file(json_path):  # if asset_data  create mode else read
        try:
            with open(json_path, "r") as read_file:
                asset_data = json.load(read_file)
                return asset_data
        except Exception as message:
            logger.error(message)
            return None

    @staticmethod
    def write_info_file(json_path, asset_data):  # create info file
        try:
            recorded_info = {"name": asset_data["name"],
                             "asset_id": asset_data["asset_id"],
                             "tags": asset_data["tags"],
                             "description": asset_data["description"]}

            with open(json_path, 'w') as outfile:
                json.dump(recorded_info, outfile, indent=4)
            logger.debug("Created json: " + json.dumps(recorded_info))
            return True
        except Exception as message:
            logger.error(message)
            return False

    @staticmethod
    def recognize_asset(path, db_model):
        """
        gets information about an existing asset, paths from info and files from folders
        """
        try:
            asset_json = Asset.dir_names(path)["asset_json"]
            asset_data = Asset.info_file(asset_json)
            asset_data["path"] = path

            asset_data['icon'] = ""
            if os.path.exists(Asset.dir_names(path)["icon"]):
                asset_data['icon'] = Asset.dir_names(path)["icon"]

            asset_data["asset_id"] = db_model.find_asset(path=path)[0]
            asset_content = os.listdir(Asset.dir_names(path)["content_folder"])
            asset_data["scenes"] = [Asset.dir_names(path)["content_folder"] + "/" + x for x in asset_content]
            gallery_content = os.listdir(Asset.dir_names(path)["gallery_folder"])
            asset_data["gallery"] = [Asset.dir_names(path)["gallery_folder"] + "/" + x for x in gallery_content]
            logger.debug(json.dumps(asset_data))
            return asset_data
        except Exception as message:
            logger.error(message)
            return False

    @staticmethod
    def delete_asset(name, path):
        try:
            del_folder = get_library_path() + "/" + DELETED_ASSET_FOLDER
            if not os.path.exists(del_folder):
                os.mkdir(del_folder)
            time = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
            os.rename(path, path + "_" + time)
            shutil.move(path + "_" + time, del_folder)
            logger.debug("Asset " + name + " deleted successfully")
            return True
        except Exception as message:
            logger.error(message)
            return False

    def asset_data(self):
        asset_data = dict()
        asset_data["name"] = self.name
        asset_data["path"] = self.path
        asset_data["asset_id"] = self.asset_id
        asset_data["icon"] = self.icon
        asset_data["tags"] = self.tags
        asset_data["description"] = self.description
        asset_data["content_folder"] = self.content_folder
        asset_data["gallery_folder"] = self.gallery_folder
        asset_data["scenes"] = self.scenes
        asset_data["gallery"] = self.gallery

        return asset_data

    @staticmethod
    def dir_names(in_path):
        try:
            out = dict()
            out["info_folder"] = in_path + "/" + INFO_FOLDER
            out["content_folder"] = in_path + "/" + CONTENT_FOLDER
            out["gallery_folder"] = in_path + "/" + GALLERY_FOLDER
            out["asset_json"] = in_path + "/" + INFO_FOLDER + "/data.txt"
            out["icon"] = in_path + "/" + INFO_FOLDER + "/icon.png"
            return out
        except Exception as message:
            logger.error(message)
            return False


if __name__ == '__main__':
    path = "U:/AssetStorage/library/food/fruit/orange2_ast/info/" + "icon.png"


