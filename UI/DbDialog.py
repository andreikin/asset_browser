# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QWidget, QFileDialog, QInputDialog, QPushButton, QApplication, QVBoxLayout

from UI.Ui_dbDialog import Ui_Dialog


class DbDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = self.setupUi(self)

        self.database = None

        self.new_button.clicked.connect(self.new_db)
        self.point_button.clicked.connect(self.point_db)
        self.cancel_button.clicked.connect(self.reject)

    def new_db(self):
        self.database = QFileDialog.getSaveFileName(self, 'Save File', filter='*.db')[0]
        self.accept()

    def point_db(self):
        self.database = QFileDialog.getOpenFileName(self, 'Open file')[0]
        self.accept()



if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    dialog = DbDialog()
    result = dialog.exec_()

    print(result, dialog.database)

    sys.exit(app.exec_())