# -*- coding: utf-8 -*-
from os import getcwd


READ_TIMEOUT = 3.5
token = "API_TOKEN"
commands = ["/start", "/help", "/settings", "/watermark", "/about", "/bio"]
file_user_data = getcwd() + "\\user_data.txt"
description = """
Hi, this is description, please check /help
"""
exception_error = """
Наложение фотографии малого размера на такую же фотографию влечет ошибку, так же она может возникнуть\n
при наложении большой фотографии на маленькую, и наоборот в особых случаях.
"""
command_crd_info = "To change location of watermark, submit a value of no more than 9999 and no less than 0." \
                   " For example input\n/crds 50 50\n/crds 150 150"
command_watermark_info = "To change the location of the watermark, input a command /watermark" \
                         " and send your watermark after it"
command_about_info = "This bot is written using python with help pyTelegramBotAPI"
