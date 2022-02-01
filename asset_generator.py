import re
import sys
from random import randint, choice

from Models import Models
from Utilities.Utilities import get_db_path

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

path_list = ['U:\\AssetStorage\\library\\buildings', 'U:\\AssetStorage\\library\\computers',
             'U:\\AssetStorage\\library\\electronics', 'U:\\AssetStorage\\library\\food\\fruit',
             'U:\\AssetStorage\\library\\food\\meat', 'U:\\AssetStorage\\library\\food',
             'U:\\AssetStorage\\library\\furniture', 'U:\\AssetStorage\\library\\items',
             'U:\\AssetStorage\\library\\Maya', 'U:\\AssetStorage\\library\\paper',
             'U:\\AssetStorage\\library\\transport\\air', 'U:\\AssetStorage\\library\\transport\\cars',
             'U:\\AssetStorage\\library\\transport\\space', 'U:\\AssetStorage\\library\\transport',
             'U:\\AssetStorage\\library\\vegetation\\grass', 'U:\\AssetStorage\\library\\vegetation\\tree',
             'U:\\AssetStorage\\library\\vegetation', 'U:\\AssetStorage\\library\\weapon']


image_list = [f'D:/work/_pythonProjects/asset_manager/images/im_{x:02}.PNG' for x in range(32)]


def asset_generator(inp_text):
    word_list = [x for x in re.findall(r'[\dA-z_]+', inp_text) if len(x) > 3]
    out_dict = dict()
    out_dict['name'] = choice(word_list)
    out_dict['path'] = choice(path_list)
    out_dict['image'] = choice(image_list)
    out_dict['tags'] = [choice(word_list) for x in range(randint(1, 5))]
    out_dict['description'] = ' '.join([choice(word_list) for x in range(10)])
    out_dict['scenes'] = 'D://' + choice(word_list) + "/" + choice(word_list) + ".mb"
    return out_dict


db_path = get_db_path()
Models.initialize(db_path)

print(db_path)

# for i in range(200):
#     kwargs = asset_generator(inp_text)
#     Models.add_asset(**kwargs)
#     print(i)