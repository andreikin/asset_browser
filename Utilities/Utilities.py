import os
import tempfile
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from Utilities.Logging import logger


def get_library_path():
    file_path = os.path.join(tempfile.gettempdir(), 'asset_manager_settings.ini')
    settings = QSettings(file_path, QSettings.IniFormat)
    if not settings.contains("db settings") or settings.value("db settings") == "":
        settings.setValue("db settings", "")
    logger.debug("lib_path :" + settings.value("db settings"))
    return settings.value("db settings")


def get_tags_from_path(path):
    """
    Function to get tags from the folder or folders in which the asset is located
    """
    db_path = get_library_path()
    tags = path.split(db_path)[-1].split("/")
    return [x for x in tags if x][:-1]


def convert_path_to_local(path):
    """
    return local path to asset
    """
    if not path:
        return None

    path = path.replace("//", "/") # remove "//"

    if path[-1] in ["/", "\\"]:
        path = path[:-1]  # remove "\\" or "\" at the end

    local_path = path.split(get_library_path())[-1]
    local_path = os.path.dirname(local_path) if local_path[-4:] == "_ast" else local_path
    return local_path


def convert_path_to_global(path):

    if not path[0] in ["/", "\\"]:
        path = "/"+path
    # remove "//"
    path = path.replace("//", "/")
    # remove "\\" or "\" at the end
    if path[-1] in ["/", "\\"]:
        path = path[:-1]
    return get_library_path() + path


def set_font_size(widget, size):
    font = widget.font()
    font.setPointSize(size)
    widget.setFont(font)









if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    path = "D:/03_andrey/py_progects/asset_browser/lib//character//frog_01_ast\\"
    path = "character//"
    print("\n", convert_path_to_global(path))

    sys.exit(app.exec_())
