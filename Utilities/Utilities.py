import os
import tempfile
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication

#from Utilities.Logging import logger
from settings import IMAGE_PREVIEW_SUFFIX, DROP_MENU_WIDTH


def get_library_path():
    file_path = os.path.join(tempfile.gettempdir(), 'asset_manager_settings.ini')
    settings = QSettings(file_path, QSettings.IniFormat)
    if not settings.contains("db settings") or settings.value("db settings") == "":
        settings.setValue("db settings", "")

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

    path = path.replace("//", "/")  # remove "//"

    if path[-1] in ["/", "\\"]:
        path = path[:-1]  # remove "\\" or "\" at the end

    local_path = path.split(get_library_path())[-1]
    local_path = os.path.dirname(local_path) if local_path[-4:] == "_ast" else local_path
    return local_path


def convert_path_to_global(path):
    """
    return global path to asset
    """
    if not path[0] in ["/", "\\"]:
        path = "/" + path
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


def get_preview_images(**kwargs):
    gallery_path = kwargs.setdefault("gallery_folder", "")
    info_folder = kwargs.setdefault("info_folder", "")
    out = []
    try:
        if os.path.exists(gallery_path):
            # get gallery content
            gallery_content = os.listdir(gallery_path)
            for file in gallery_content:
                filename, file_extension = os.path.splitext(file)
                icon_path = info_folder + "/" + filename + IMAGE_PREVIEW_SUFFIX + file_extension
                image_path = gallery_path + "/" + filename + file_extension
                if not os.path.exists(icon_path):
                    image_light = QPixmap(gallery_path + "/" + file)
                    image_light = image_light.scaledToWidth(DROP_MENU_WIDTH - 45, mode=Qt.SmoothTransformation)
                    image_light.save(icon_path)
                out.append([icon_path, image_path])
        #logger.debug(out)
        return out
    except Exception as message:
        #logger.error(message)
        pass
    return out



if __name__ == '__main__':
    import sys
    # app = QApplication(sys.argv)
    # path = "U:/AssetStorage/asset_browser/Characters/Human/Torso/Girl_Torso_03_ast/gallery"
    # print(create_preview_images(path))
    # sys.exit(app.exec_())
