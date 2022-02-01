import os
import tempfile
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication
from UI.DbDialog import DbDialog


def get_db_path():
    file_path = os.path.join(tempfile.gettempdir(), 'asset_manager_settings.ini')
    settings = QSettings(file_path, QSettings.IniFormat)
    if not settings.contains("db settings") or settings.value("db settings") == "":
        dialog = DbDialog()
        result = dialog.exec_()
        if result:
            settings.setValue("db settings", dialog.database)
        else:
            sys.exit(app.exec_())
    return settings.value("db settings")


def get_tags_from_path(path):
    """
    Function to get tags from the folder or folders in which the asset is located
    """
    db_path = os.path.dirname(get_db_path())
    tags = path.split(db_path)[-1].split("/")

    return [x for x in tags if x][:-1]




if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    tags = get_tags_from_path("U:/AssetStorage/library/food/fruit/orange01_ast")
    print(tags)
    print("close____________")
    sys.exit(app.exec_())
