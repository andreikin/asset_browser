# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

from Controller.Controller import Controller
from Models import Models


def main():
    app = QApplication(sys.argv)

    # create a database model
    models = Models

    # create a controller and pass it a link to the model
    controller = Controller(models)
    controller.ui.show()

    app.exec()

if __name__ == '__main__':
    sys.exit(main())

