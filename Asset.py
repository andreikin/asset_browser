# -*- coding: utf-8 -*-
import datetime
import json
import os
import shutil
import tempfile

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from Utilities.Logging import logger
from Utilities.telegram_bot import send_message_to_bot
from Utilities.Utilities import get_library_path, rename_path_list
from settings import INFO_FOLDER, CONTENT_FOLDER, GALLERY_FOLDER, ICON_WIDTH, DELETED_ASSET_FOLDER, SFX, \
    IMAGE_PREVIEW_SUFFIX, DROP_MENU_WIDTH


class Asset:
    """
    The class defines an asset as a structure of folders and files.
    Contains methods for creating, modifying, and deleting assets
    """
    def __init__(self, in_controller, **kwargs):
        try:
            self.Controller = in_controller

            self.asset_id = kwargs.setdefault("asset_id", None)
            self.name = kwargs["name"]
            self.path = kwargs["path"]
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
            self.rename_content = self.Controller.ui.rename_checkBox.isChecked()
            logger.debug(" executed")

        except Exception as message:
            logger.error(message)

    def create(self):
        """
        Create asset file structure and write it to the database
        """
        try:
            if not self.Controller.Models.find_asset(name=self.name):

                # making folders
                for each_path in [self.path, self.asset_info_folder, self.content_folder, self.gallery_folder]:
                    if not os.path.exists(each_path):
                        os.makedirs(each_path)

                # set asset icon
                self.icon = self.create_icon("icon.png", self.icon, ICON_WIDTH)

                # add to database and record info file
                self.asset_id = self.Controller.Models.add_asset_to_db(**self.asset_data())
                self.write_info_file(self.asset_json, self.asset_data())

                # copy files
                self.Controller.ui.add_task(self.copy_files)

                # edit content names
                self.Controller.ui.add_task(self.rename_scenes)

                self.refresh_ui_after_edit()

                if self.Controller.ui.message_to_bot.isChecked():
                    send_message_to_bot(self.name, self.icon, self.path)

                logger.debug(" executed")
            else:
                self.Controller.ui.status_message("Asset with " + self.name + " name already exists!", state="ERROR")
        except Exception as message:
            logger.error(message)

    def edit(self):
        """
        Edit asset file structure and write it to the database
        """
        try:
            if self.name != self.old_asset_data["name"] and self.Controller.Models.find_asset(name=self.name):
                logger.error(" path : " + self.path + " exists")
                self.Controller.ui.status_message("Asset with " + self.name + " name already exists!", state="ERROR")
            else:
                self.edit_name()
                self.edit_path()
                self.edit_icon()

                self.write_info_file(self.asset_json, self.asset_data())
                self.Controller.Models.edit_db_asset(**self.asset_data())

                # copy files
                self.Controller.ui.add_task(self.copy_files)

                # edit content names
                self.Controller.ui.add_task(self.rename_scenes)

                self.refresh_ui_after_edit(mode=" edited")
                logger.debug(" executed")
        except Exception as message:
            logger.error(message)

    def create_icon(self, name, seurce, width):
        """
        Creating the main asset icon
        """
        try:
            if seurce:
                icon = QPixmap(seurce).scaledToWidth(width, mode=Qt.SmoothTransformation)
                asset_icon_path = self.path + "/" + INFO_FOLDER + "/" + name
                icon.save(asset_icon_path)
                # if image from temp folder remove it
                if tempfile.gettempdir().replace("\\", "/") in seurce:
                    os.remove(seurce)
                return asset_icon_path
        except Exception as message:
            logger.error(message)

    def edit_name(self):
        """
        When editing the name of an asset, it changes the name of the folders,
        the information in the database, and the information file
        """
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
            asset_data = self.get_info_file(asset_json)
            asset_data["name"] = self.name
            self.write_info_file(asset_json, asset_data)

            logger.debug(" executed")
        except Exception as message:
            logger.error(message)
            return None

    def edit_path(self):
        """
        Move asset to another directory
        """
        if self.path != self.old_asset_data["path"]:
            try:
                shutil.move(self.old_asset_data["path"], self.path)
                for i in range(len(self.gallery)):
                    self.gallery[i] = self.gallery[i].replace(self.old_asset_data["path"], self.path)
                for i in range(len(self.scenes)):
                    self.scenes[i] = self.scenes[i].replace(self.old_asset_data["path"], self.path)
            except Exception as message:
                logger.error(message)

    def edit_icon(self):
        """
        icon update or delete
        """
        icon_default_path = Asset.dir_names(self.path)["icon"]
        if self.icon != icon_default_path:
            # delete the old icon if there is no new path or if the new path is not equal to the old one
            if not self.icon and os.path.exists(icon_default_path):
                os.remove(icon_default_path)
            if self.icon:
                self.icon = self.create_icon("icon.png", self.icon, ICON_WIDTH)

    def get_old_asset_data(self):
        """
        when changing the main attributes of asset, it takes the old data from the database
        """
        out = dict()
        try:
            out["asset_id"], out["name"], out["path"] = self.Controller.Models.find_asset(id=self.asset_id)
            logger.debug(" executed")
        except Exception as message:
            logger.error(message)
        return out

    def copy_files(self):
        """
        Creates a stream for copying files and a stream for the progress bar
        """
        try:
            copy_list = self.prepare_files_for_copy()
            if copy_list:
                self.Controller.ui.copy_progress_bar.show()
                for source_files, destination_files in copy_list:
                    self.Controller.ui.copy_function.copy(source_files, destination_files)
                self.create_preview_images()
                self.Controller.ui.copy_progress_bar.hide()
                logger.debug(" executed")
        except Exception as message:
            logger.error(message)

    def prepare_files_for_copy(self):
        """
        Sorts files - leave unchanged, copy or delete. Deletes here
        """
        try:
            copy_list = []
            for source_files, destination_folder in [(self.scenes, self.content_folder),
                                                     (self.gallery, self.gallery_folder)]:
                destination_files = [destination_folder + "/" + x for x in os.listdir(destination_folder)]
                while source_files:
                    curent_file = source_files.pop()
                    if curent_file in destination_files:
                        destination_files.remove(curent_file)  # remove current_file from variable destination_files
                    else:
                        file_name = os.path.basename(curent_file)
                        copy_list.append([curent_file, destination_folder + "/" + file_name])
                self.del_file_and_its_icon(destination_files)
            return copy_list
        except Exception as message:
            logger.error(message)

    def del_file_and_its_icon(self, files):
        """
        Deletes the gallery file and its icon
        """
        try:
            for curent_file in files:
                os.remove(curent_file)
                # if file has icon - delete it
                filepath, file_extension = os.path.splitext(curent_file)
                file = os.path.basename(filepath)
                icon_path = self.asset_info_folder + "/" + file + IMAGE_PREVIEW_SUFFIX + file_extension
                if os.path.exists(icon_path):
                    os.remove(icon_path)
        except Exception as message:
            logger.error(message)

    @staticmethod
    def get_info_file(json_path):
        """
        read info file
        """
        try:
            with open(json_path, "r") as read_file:
                asset_data = json.load(read_file)
                return asset_data
        except Exception as message:
            logger.error(message)
            return None

    @staticmethod
    def write_info_file(json_path, asset_data):
        """
        create info file
        """
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
            asset_data = Asset.get_info_file(asset_json)
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

    def refresh_ui_after_edit(self, mode=" created"):
        """
        Open the folder with the asset in the ui
        """
        self.Controller.get_from_folder(os.path.dirname(self.path) + "/")
        self.Controller.ui.search_lineEdit.setText("")
        self.Controller.ui.clear_form()
        self.Controller.ui.status_message("Asset " + self.name + mode + " successfully!", )

    @staticmethod
    def delete_asset(name, path):
        """
        When an asset is deleted, the structure is moved to a special
        folder for deleted assets. Delete time added to folder name
        """
        try:
            del_folder = get_library_path() + "/" + DELETED_ASSET_FOLDER
            if not os.path.exists(del_folder):
                os.mkdir(del_folder)
            time = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")

            path = shutil.move(path, del_folder)
            os.rename(path, path + "_" + time)
            logger.debug(name + " deleted successfully")
            return True
        except Exception as message:
            logger.error(message)
            return False

    def asset_data(self):
        """
        Returns the values of the main attributes of an asset
        """
        asset_data = dict()
        asset_data["name"] = self.name
        asset_data["path"] = self.path
        asset_data["asset_id"] = self.asset_id
        asset_data["icon"] = self.icon
        asset_data["tags"] = self.tags
        asset_data["description"] = self.description
        asset_data["info_folder"] = self.asset_info_folder
        asset_data["content_folder"] = self.content_folder
        asset_data["gallery_folder"] = self.gallery_folder
        asset_data["scenes"] = self.scenes
        asset_data["gallery"] = self.gallery
        asset_data["rename_content"] = self.rename_content
        return asset_data

    @staticmethod
    def dir_names(in_path):
        """
        Returns the paths to the main folders of the asset and to the info file
        """
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

    def create_preview_images(self):
        """
        Create icons for widget gallery
        """
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
                                                                mode=Qt.SmoothTransformation)
                        image_light.save(icon_path)
        except Exception as message:
            logger.error(message)

    def rename_scenes(self):
        """
        Rename asset content if necessary
        """
        try:
            if self.rename_content:
                if self.content_folder[-1] != '/':
                    self.content_folder = self.content_folder + '/'

                scenes_list = os.listdir(self.content_folder)
                type_dict = {}
                for i in scenes_list:
                    file, ext = i.split('.')
                    if ext.lower() in type_dict:
                        type_dict[ext.lower()].append(file)
                    else:
                        type_dict[ext.lower()] = [file]

                for key in type_dict.keys():
                    n = len(type_dict[key])
                    if n == 1:
                        os.rename(self.content_folder + type_dict[key][0] + '.' + key,
                                  self.content_folder + self.name + '.' + key)
                    else:
                        for i in range(1, len(type_dict[key]) + 1):
                            os.rename(self.content_folder + type_dict[key][i - 1] + '.' + key,
                                      self.content_folder + self.name + '_{0:02d}.'.format(i) + key)
                logger.debug(" executed")
        except Exception as message:
            logger.error(message)