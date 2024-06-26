# -*- coding: utf-8 -*-

import telepot
import os

TESTING = False

if TESTING:
    CHAT_ID = 476369950
else:
    CHAT_ID = -1001617856660

TOKEN = '550024543:AAGGNxWOUXR2xzj0JAJ1wxq3HthRoh38Gw8'
PARSE_MODE = 'Markdown'
LIMIT_SIZE = 5242879


def send_message_to_bot(asset_name, icon, folder):
    message = f"In database added new asset:\n"
    message += f'`Name:` *{asset_name}*\n'
    message += f'`Folder:` *{folder}*\n'

    bot = telepot.Bot(TOKEN)
    if icon:
        FILE_SIZE = os.stat(icon).st_size
        if FILE_SIZE <= LIMIT_SIZE:
            with open('%s' % icon, 'rb') as f:
                bot.sendPhoto(CHAT_ID, f, caption=message, parse_mode=PARSE_MODE)
        else:
            print('File size more then 5mb, reduce file size!!!')
    else:
        bot.sendMessage(CHAT_ID, message, parse_mode='Markdown')


if __name__ == '__main__':

    pic = 'C:/Users/avbeliaev/Desktop/Backpack_03_ast/info/icon.png'
    name = r'Backpack_04'
    folder = r'C:/Users/avbeliaev/Desktop/gerl_robot_02_ast'
    send_message_to_bot(name, pic, folder)
