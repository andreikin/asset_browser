# -*- coding: utf-8 -*-
import os

from peewee import *
from Utilities.Logging import logger
from Utilities.Utilities import get_library_path

"""
The module Models.py defines the structure of the database and contains 
functions for finding assets by tags and getting a tag cloud
"""

data_base = SqliteDatabase(None)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = data_base  # model will use the database 'assets.db'


class Asset(BaseModel):
    name = CharField()
    path = CharField()
    icon = TextField()
    # description = TextField()
    # scenes = TextField()
    # tags = TextField()  # test:


class Tag(BaseModel):
    name = CharField()
    asset_id = ForeignKeyField(Asset)


def initialize(lib_path):
    from settings import DATABASE_NAME
    if not lib_path:
        logger.error("Database path required for initialization")
        return False
    else:
        db_path = lib_path + "/" + DATABASE_NAME
        if not os.path.exists(db_path):
            logger.error("Database path " + db_path + " not exists")
            return False
        else:
            try:
                data_base.init(db_path)
                data_base.create_tables([Asset, Tag])
                logger.debug("Database " + db_path + "  initialized successfully!")
                return True
            except Exception as message:
                logger.error(message)
                return False


def add_asset_to_db(**kwargs):
    tags = kwargs.pop('tags')
    try:
        db_asset = Asset.create(**kwargs)
        for tag in tags:
            Tag.create(name=tag, asset_id=db_asset)
        logger.debug("Asset added to database")
        return db_asset.id
    except Exception as message:
        logger.error(message)
        return False


def find_assets_by_tag_list(tag_list):
    out = []
    # get all assets matching by name
    quest_string = ['(Asset.name == "' + x + '")' for x in tag_list]
    quest_string = " | ".join(quest_string)
    quest = 'Asset.select().where(' + quest_string + ')'
    try:
        found_assets = eval(quest)
        if found_assets:
            for asset in found_assets:
                out.append(asset)
    except Exception as message:
        logger.error(message)
    # get all assets matching by tag
    tag_quest_string = ['(Tag.name == "' + x + '")' for x in tag_list]
    tag_quest_string = " | ".join(tag_quest_string)
    quest = 'Tag.select().where(' + tag_quest_string + ')'
    try:
        assets_id = eval(quest)
        logger.debug("Set quest to db : " + quest)
        for id in assets_id:
            asset = Asset.get(Asset.id == id.asset_id)
            if asset not in out:
                out.append(asset)
    except Exception as message:
        logger.error(message)
    return out


def find_tags_by_asset_list(asset_list):
    out = []
    tag_quest_string = ['(Tag.asset_id == "' + str(x.id) + '")' for x in asset_list]
    tag_quest_string = " | ".join(tag_quest_string)
    quest = 'Tag.select().where(' + tag_quest_string + ')'
    try:
        tags = eval(quest)
        for tag in tags:
            if tag.name not in out:
                out.append(tag.name)
    except Exception as message:
        logger.error(message)
    return out


def find_asset_by_path(path):
    logger.debug(path)
    res = Asset.select().where(Asset.path == path)
    return res


def is_asset_in_db(name):
    if Asset.select().where(Asset.name == name):
        return True
    else:
        return False


def delete_asset(asset_name):
    try:
        asset_obj = Asset.get(Asset.name == asset_name)
        for tag in Tag.select().where(Tag.asset_id == asset_obj):
            tag.delete_instance()
        asset_obj.delete_instance()
        return True
    except Exception as message:
        logger.error(message)
        return False


def edit_db_asset(**kwargs):
    try:
        asset_obj = Asset.get(Asset.name == kwargs["name"])
        # edit tags
        for tag in Tag.select().where(Tag.asset_id == asset_obj):
            tag.delete_instance()
        for tag in kwargs["tags"]:
            Tag.create(name=tag, asset_id=asset_obj)
        # edit icon
        asset_obj.icon = kwargs["icon"]
        # edit path
        asset_obj.path = kwargs["path"]
        asset_obj.save()

        logger.debug(" executed")
    except Exception as message:
        logger.error(message)
        return False


def rename_directory(old_path, new_path, old_name, new_name):
    try:
        renamed_paths = []
        for asset_obj in Asset.select():
            if old_path in asset_obj.path:
                path = asset_obj.path.replace(old_path, new_path)
                asset_obj.path = path
                asset_obj.save()
                renamed_paths.append(path)

        logger.debug("Path " + old_path + " renamed to " + new_path)
        return renamed_paths
    except Exception as message:
        logger.error(message)
        return False

def get_all_from_folder(path):
    try:
        out = []
        for asset_obj in Asset.select():
            if path in asset_obj.path:
                out.append(asset_obj)
        logger.debug(out)
        return out
    except Exception as message:
        logger.error(message)
        return False


if __name__ == '__main__':
    from settings import DATABASE_NAME

    db_path = get_library_path()
    initialize(db_path)

    path = "U:/AssetStorage/library/super_food"

    print(get_all_from_folder(path))
