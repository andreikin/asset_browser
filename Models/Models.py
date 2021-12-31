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
    print('added ', kwargs)
    tags = kwargs.pop('tags')
    if not kwargs["name"] in tags:
        tags.append(kwargs["name"])
    kwargs['tags'] = ' '.join(tags) # test
    asset = Asset.create(**kwargs)
    for tag in tags:
        Tag.create(name=tag, asset_id=asset)


def find_asset_by_tag_list(tag_list):
    out = []
    for in_tag in tag_list:
        for asset in Asset.select().where(Asset.name == in_tag):
            if asset not in out:
                out.append(asset)
        for tag in Tag.select().where(Tag.name == in_tag):
            asset = Asset.get(Asset.id == tag.asset_id)
            if asset not in out:
                out.append(asset)
    return out


def find_tag_by_asset(asset):
    asset = Asset.get(Asset.name == asset)
    out = []
    for tag in Tag.select().where(Tag.asset_id == asset):
        out.append(tag)
    return out


def delete_asset(asset_id):
    asset = Asset.get(Asset.id == asset_id)
    for tag in find_tag_by_asset(asset.name):
        tag.delete_instance()
    asset.delete_instance()


