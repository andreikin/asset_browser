import os
import re
import tempfile
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSettings, Qt, QObject
from PyQt5.QtGui import QPixmap
from Utilities.Logging import logger
from settings import IMAGE_PREVIEW_SUFFIX, DROP_MENU_WIDTH, SFX, ICON_FORMATS_PATTERN

def copy_file(src, dst, progress_bar=None):
    """
    copies file by parts with changing the progress bar
    """
    try:
        path_name = os.path.dirname(dst)
        if not os.path.exists(path_name):
            os.makedirs(path_name)

        with open(src, 'rb') as src_file, open(dst, 'wb') as dst_file:
            buffer = os.stat(src).st_size // 100
            percent = 0
            while True:
                buf = src_file.read(buffer)
                bytes_written = dst_file.write(buf)
                percent += 1
                if progress_bar and percent <= 100:
                    progress_bar.setValue(percent)
                    #QtWidgets.qApp.processEvents()
                if bytes_written < len(buf) or bytes_written == 0:
                    break
    except Exception as message:
        print(message)


class CopyWithProgress(QObject):
    progress_bar_signal = QtCore.pyqtSignal(int)

    def copy(self, src, dst):
        try:
            path_name = os.path.dirname(dst)
            if not os.path.exists(path_name):
                os.makedirs(path_name)

            with open(src, 'rb') as src_file, open(dst, 'wb') as dst_file:
                buffer = os.stat(src).st_size // 25
                percent = 0
                while True:
                    buf = src_file.read(buffer)
                    bytes_written = dst_file.write(buf)
                    percent += 4
                    self.progress_bar_signal.emit(percent)
                    QtWidgets.qApp.processEvents()
                    if bytes_written < len(buf) or bytes_written == 0:
                        break
        except Exception as message:
            print(message)

def get_library_path():
    """
    return library path
    """
    file_path = os.path.join(tempfile.gettempdir(), 'asset_manager_settings.ini')
    settings = QSettings(file_path, QSettings.IniFormat)
    if not settings.contains("db settings") or settings.value("db settings") == "":
        settings.setValue("db settings", "")

    return settings.value("db settings")


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


def rename_path_list(old_name, new_name, path_list):
    """
    renames multiple paths when changing the name of an asset
    """
    out = []
    for path in path_list:
        out.append(path.replace("/" + old_name + SFX + "/", "/" + new_name + SFX + "/"))
    return out


def remove_non_unique_tags(tags_list):
    out = []
    for tag in tags_list:
        if tag not in out:
            out.append(tag.lower())
    return out


def get_preview_images(**kwargs):
    gallery_path = kwargs.setdefault("gallery_folder", "")
    info_folder = kwargs.setdefault("info_folder", "")
    out = []
    try:
        if os.path.exists(gallery_path):
            # get gallery content and verify it
            gallery_content = [x for x in os.listdir(gallery_path) if re.search(ICON_FORMATS_PATTERN, x)]
            for file in gallery_content:
                filename, file_extension = os.path.splitext(file)
                icon_path = info_folder + "/" + filename + IMAGE_PREVIEW_SUFFIX + file_extension
                image_path = gallery_path + "/" + filename + file_extension
                if not os.path.exists(icon_path):
                    image_light = QPixmap(gallery_path + "/" + file)
                    image_light = image_light.scaledToWidth(DROP_MENU_WIDTH - 45, mode=Qt.SmoothTransformation)
                    image_light.save(icon_path)
                out.append([icon_path, image_path])
        # logger.debug(out)
        return out
    except Exception as message:
        logger.error(message)
    return out


if __name__ == '__main__':
    pass
