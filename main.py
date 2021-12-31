# -*- coding: utf-8 -*-
import re
import sys
from random import randint, choice
from PyQt5.QtWidgets import QApplication, QPushButton
from Controller.Controller import Controller
from Models import Models


def main():
    app = QApplication(sys.argv)

    # create a model
    models = Models

    # create a controller and pass it a link to the model
    controller = Controller(models)
    controller.ui.show()
    app.exec()

















if __name__ == '__main__':
    inp_text = """
    The Maya Help is accessible from the Help menu of Maya. There are two versions of the Maya Help: the Online default 
    version, accessed via the internet, and an Offline version that you can download and install locally. Both versions 
    appear in your Web browser and give you complete access to the Maya documentation. 
    The online Help is published as part of the Autodesk Knowledge Network, the place to go for Autodesk Support,  
    and Community resources. Sign in using your Autodesk account and participate. For more information on creating an  
    see Creating an  Account. Search the online help The online version of the Help has multiple features that let 
    you participate  Online community. You can leave comments, share pages on social media, and participate in 
    discussions with other users. Searching the online help provides you not only with access to the full Maya doc 
    matches from other web sites, like the Autodesk forums and YouTube channels, in your search. Your results are ranked 
    according to the number of occurrences of the keyword(s) and are listed from the highest rank to the lowest.  
    Each match contains contextual details, including an excerpt of text, the name of its source, and the date it was 
    last updated, so you can quickly navigate your results
    """

    def asset_generator(inp_text):
        word_list = [x for x in re.findall(r'[\dA-z_]+', inp_text) if len(x) > 3]
        out_dict = dict()
        out_dict['name'] = choice(word_list)
        out_dict['path'] = 'D://' + choice(word_list) + "/" + choice(word_list)
        out_dict['image'] = 'D://' + choice(word_list) + "/" + choice(word_list) + ".png"
        out_dict['tags'] = [choice(word_list) for x in range(randint(1, 5))]
        out_dict['description'] = ' '.join([choice(word_list) for x in range(10)])
        out_dict['scenes'] = 'D://' + choice(word_list) + "/" + choice(word_list) + ".mb"
        return out_dict

    # for _ in range (100):
    #     kwargs = asset_generator(inp_text)
    #     Models.add_asset(**kwargs)



    sys.exit(main())

