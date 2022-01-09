# -*- coding: utf-8 -*-
from peewee import *

data_base = SqliteDatabase('assets.db')


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = data_base  # model will use the database 'assets.db'


class Asset(BaseModel):
    name = CharField()
    path = CharField()
    image = TextField()
    description = TextField()
    scenes = TextField()
    tags = TextField()  # test:


class Tag(BaseModel):
    name = CharField()
    asset_id = ForeignKeyField(Asset)


Asset.create_table()
Tag.create_table()


def add_asset(**kwargs):
    tags = kwargs.pop('tags')
    if not kwargs["name"] in tags:
        tags.append(kwargs["name"])
    kwargs['tags'] = ' '.join(tags)  # test
    asset = Asset.create(**kwargs)
    for tag in tags:
        Tag.create(name=tag, asset_id=asset)


def find_assets_by_tag_list(tag_list):
    out = []
    """get all assets matching by name"""
    quest_string = ['(Asset.name == "' + x + '")' for x in tag_list]
    quest_string = " | ".join(quest_string)
    quest = 'Asset.select().where(' + quest_string + ')'
    assets = eval(quest)
    if assets:
        for asset in assets:
            out.append(asset)
        """get all assets matching by tag"""
        tag_quest_string = ['(Tag.name == "' + x + '")' for x in tag_list]
        tag_quest_string = " | ".join(tag_quest_string)
        quest = 'Tag.select().where(' + tag_quest_string + ')'
        assets_id = eval(quest)
        for id in assets_id:
            asset = Asset.get(Asset.id == id.asset_id)
            if asset not in out:
                out.append(asset)
    return out


def find_tags_by_asset_list(asset_list):
    out = []
    tag_quest_string = ['(Tag.asset_id == "' + str(x.id) + '")' for x in asset_list]
    tag_quest_string = " | ".join(tag_quest_string)
    quest = 'Tag.select().where(' + tag_quest_string + ')'
    tags = eval(quest)
    for tag in tags:
        if tag.name not in out:
            out.append(tag.name)
    return out


def delete_asset(asset_id):
    asset = Asset.get(Asset.id == asset_id)
    for tag in Tag.select().where(Tag.asset_id == asset):
        tag.delete_instance()
    asset.delete_instance()

if __name__ == '__main__':
    pass
    assets = find_assets_by_tag_list(["Maya2", "Help2"])
    for asset in assets:
        print(asset, asset.name)