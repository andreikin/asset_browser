# -*- coding: utf-8 -*-
import os
from settings import COMPLEX_SEARCH_SIGNS
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
        try:
            data_base.init(db_path)
            data_base.connect()
            data_base.create_tables([Asset, Tag])
            logger.debug("Database " + db_path + "  initialized successfully!")
            return True
        except Exception as message:
            logger.error(message)
            return False


def add_asset_to_db(**kwargs):
    tags = kwargs.pop('tags')
    kwargs['icon'] = ""
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
    try:
        has_and_attr = any([x in tag_list for x in COMPLEX_SEARCH_SIGNS])
        # if the asset you are looking for must include all tags
        if has_and_attr:
            tag_list = [x for x in tag_list if x not in COMPLEX_SEARCH_SIGNS]
            res_set = set()
            for i, tag in enumerate(tag_list):
                quest_rez = Tag.select().where(Tag.name == tag)
                if not i:
                    res_set = set([x.asset_id for x in quest_rez])
                else:
                    res_set = res_set & set([x.asset_id for x in quest_rez])
            out = list(res_set)
        else:
            # if the asset you are looking for must include one of the tags
            tag_quest_string = ['(Tag.name == "' + x + '")' for x in tag_list]
            tag_quest_string = " | ".join(tag_quest_string)
            quest = 'Tag.select().where(' + tag_quest_string + ')'
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
    # limiting the number of assets for the normal operation of the recursive tag search
    asset_list = asset_list[:20] if len(asset_list) > 20 else asset_list

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


def find_asset(id=None, name=None, path=None):
    try:
        asset = None
        if id:
            asset = Asset.select().where(Asset.id == id).get()
        if name:
            asset = Asset.select().where(Asset.name == name).get()
        if path:
            asset = Asset.select().where(Asset.path == path).get()
        if asset:
            return asset.id, asset.name, asset.path
        else:
            return None
    except Exception as message:
        logger.error(message)
        return None


def delete_asset(asset_name):
    try:
        asset_obj = Asset.get(Asset.name == asset_name)
        for tag in Tag.select().where(Tag.asset_id == asset_obj):
            tag.delete_instance()
        asset_obj.delete_instance()
        logger.error("Deleted asset " + asset_obj.name)
        return True
    except Exception as message:
        logger.error(message)
        return False


def edit_db_asset(**kwargs):
    try:
        asset_obj = Asset.get(Asset.id == kwargs["asset_id"])
        # edit tags
        if kwargs.setdefault("tags", None):
            for tag in Tag.select().where(Tag.asset_id == asset_obj):
                tag.delete_instance()
            for tag in kwargs["tags"]:
                Tag.create(name=tag, asset_id=asset_obj)
        # edit name
        if kwargs.setdefault("name", None):
            asset_obj.name = kwargs["name"]
        # edit path
        if kwargs.setdefault("path", None):
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

def add_asset_to_other_db(data, db_path):
    data_base_new = SqliteDatabase(db_path)

    class BaseModel_new(Model):
        id = PrimaryKeyField(unique=True)

        class Meta:
            database = data_base_new  # model will use the database 'assets.db'

    class Asset(BaseModel_new):
        name = CharField()
        path = CharField()
        icon = TextField()

    class Tag(BaseModel_new):
        name = CharField()
        asset_id = ForeignKeyField(Asset)

    Asset.create_table()
    Tag.create_table()

    tags = data['tags']
    data['icon'] = ""
    try:
        if data['name'] in [x.name for x in Asset.select()]:
            logger.error(f'Asset named {data["name"]} already exists in the database and cannot be added.')
            return False

        db_asset = Asset.create(**data)
        for tag in tags:
            Tag.create(name=tag, asset_id=db_asset)

        return db_asset.id
    except Exception as message:
        logger.error(message)

if __name__ == '__main__':
    from settings import DATABASE_NAME
    db_path = get_library_path()
    data_base.init(os.path.join(db_path, "database.db"))

    tag_list = ["head", "mgs"]
    super_list = []


    assets_with_tags = Asset.select(Asset).join(Tag).where(Tag.name=="head")

    # for tag in tag_list:
    #     quest_rez = Tag.select().where(Tag.name == tag)
    #     super_list.append([x.asset_id.id for x in quest_rez])
    #     print(len([x.asset_id.id for x in quest_rez]))

    # assets_with_tags = (Asset.select(Asset).join(Tag, on=(Tag.asset_id == Asset.id))
    # )
    print(len(assets_with_tags))
    print([x.name for x in assets_with_tags])