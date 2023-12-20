# fix db exist error
import subprocess
import tempfile
from pathlib import Path

VERSION = "1.1.4"

""" ui settings"""
DROP_MENU_WIDTH = 350
COLUMN_WIDTH = 140  # asset WIDGET width
SPACING = 10  # space between asset icons
ICON_WIDTH = 150  # asset icons width
START_WINDOW_SIZE = [1700, 900]
FONT_SIZE = 9

ASSETS_IN_ONE_STEP = 10  # number of assets loaded at a time

""" name of assets folders"""
INFO_FOLDER = "info"
CONTENT_FOLDER = "content"
GALLERY_FOLDER = "gallery"
SFX = "_ast"  # suffix for base asset folders
DATABASE_NAME = "database.db"
DELETED_ASSET_FOLDER = "deleted_assets"
DATABASE_PATH = 'U:/AssetStorage/asset_browser'

"""over"""
ICON_FORMATS_PATTERN = ".PNG$|.png$|.jpg$|.JPG$"
IMAGE_PREVIEW_SUFFIX = "_light"
LOGGING_TO_fILE = False

"""help pdf url"""
URL = 'https://docs.yandex.ru/docs/view?url=ya-disk-public%3A%2F%2F55Vw4e8HmjdDD9QK6tXu8KCtm6HsILLZWg7JuwU' \
      '%2B2daXO6D6zqBO9YueM6AiSkliq%2FJ6bpmRyOJonT3VoXnDag%3D%3D&name=Asset_Browser_User_manual.pdf '

if __name__ == '__main__':
    subprocess.Popen(f'explorer "{Path(tempfile.gettempdir())}"')