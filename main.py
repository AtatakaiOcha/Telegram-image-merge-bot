# -*- coding: utf-8 -*-
import config
import telebot
import fileinput
import os
import sys
import re

S_WATERMARK = 1
CRD = [0, 0, S_WATERMARK]
USER_IDS = {}
bot = telebot.TeleBot(config.token)
command = config.commands
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row(command[1], command[2])
keyboard.row(command[3], command[4], command[5])
file = config.file_user_data


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if str(user_id) not in open(file).read():
        file_user_id(user_id, CRD)
    bot.send_message(user_id, config.description, timeout=config.READ_TIMEOUT, reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def handle_help(message):
    user_id = message.from_user.id
    bot.send_message(user_id, config.command_crd_info, timeout=config.READ_TIMEOUT, reply_markup=keyboard)
    bot.send_message(user_id, config.command_watermark_info, timeout=config.READ_TIMEOUT, reply_markup=keyboard)


@bot.message_handler(commands=['about'])
def handle_bio(message):
    user_id = message.from_user.id
    bot.send_message(user_id, config.command_about_info, timeout=config.READ_TIMEOUT, reply_markup=keyboard)


@bot.message_handler(commands=['watermark'])
def handle_watermark(message):
    user_id = message.from_user.id
    bot.send_message(user_id, f"Send watermark image", timeout=config.READ_TIMEOUT)
    try:
        crd = file_read_user_data(user_id)
        crd = crd.get(user_id)
        crd[2] = 0
        file_overwrite_user_data(user_id, crd)
    except Exception as e:
        print(e)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def change_coordination(message):
    user_id = message.from_user.id
    check_command_crds = re.compile(r"[/crds][ ][1-9]\d{0,3}[ ][1-9]\d{0,3}$")
    if check_command_crds.search(message.text):
        try:
            crd = message.text.split(" ")
            crd[1] = int(crd[1])
            crd[2] = int(crd[2])
            USER_IDS.update({user_id: [crd[1], crd[2], S_WATERMARK]})
            new_crd = USER_IDS.get(user_id)
            file_overwrite_user_data(user_id, new_crd)
            bot.send_message(user_id, f"Successfully changed to [{crd[1]}:{crd[2]}]", timeout=config.READ_TIMEOUT)
        except ValueError as e:
            bot.send_message(user_id, f"Exception:{e.__class__.__name__}", timeout=config.READ_TIMEOUT)
    elif "/settings" in message.text:
        pass
    elif "/bio" in message.text:
        pass
    elif "/watermark" in message.text:
        crd = file_read_user_data(user_id)
        crd = crd.get(user_id)
        crd[2] = 1
        file_overwrite_user_data(user_id, crd)
    else:
        bot.send_message(user_id, f"Invalid command", timeout=config.READ_TIMEOUT)


@bot.message_handler(content_types=['photo'])
def handler_image(message):
    user_id = message.from_user.id
    user = file_read_user_data(user_id)
    try:
        if user[user_id][2] == 0:
            download_watermark_image(message)
        if user[user_id][2] == 1:
            download_image(message)
    except Exception as e:
        bot.send_message(user_id, f"Exception:{e.__class__.__name__}", timeout=config.READ_TIMEOUT)


def download_watermark_image(message):
    user_id = message.from_user.id
    user = file_read_user_data(user_id)
    if user[user_id][2] == 0:
        try:
            USER_IDS.update({user_id: [user[user_id][0], user[user_id][1], S_WATERMARK]})
            new_crd = USER_IDS.get(user_id)
            file_overwrite_user_data(user_id, new_crd)
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = os.getcwd() + "\\watermark_images\\" + str(user_id) + ".jpg"
            from pil_watermark import merge_watermark
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
                new_file.close()
                bot.reply_to(message, "Successfully changed to this")
                reply_photo = open(src, 'rb')
                bot.send_photo(user_id, reply_photo)
        except Exception as e:
            bot.send_message(user_id, f"Exception:{e.__class__.__name__}",
                             timeout=config.READ_TIMEOUT)
        print(USER_IDS)


def download_image(message):
    user_id = message.from_user.id
    user = file_read_user_data(user_id)
    if user[user_id][2] == 1:
        try:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            crd = file_read_user_data(user_id)
            crd = crd.get(user_id)
            src = os.getcwd() + "\\merged_images\\" + message.photo[1].file_id + ".jpg"
            from pil_watermark import merge_watermark
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
                reply_photo = merge_watermark(src, crd, user_id)
                new_file.close()
                bot.reply_to(message, "download_image")
                reply_photo = open(src, 'rb')
                bot.send_photo(user_id, reply_photo)
        except Exception as e:
            bot.send_message(user_id, f"Exception:{e.__class__.__name__}", timeout=config.READ_TIMEOUT)
            bot.send_message(user_id, f"{config.exception_error}", timeout=config.READ_TIMEOUT)


def file_user_id(user_id, crd):
    data = {user_id: crd}
    if os.access(file, os.W_OK):
        with open(file, "a") as out:
            for key, value in zip(data.keys(), data.values()):
                out.write(f"{key}:{value[0]}-{value[1]}-{value[2]}\n")
                out.close()


def file_overwrite_user_data(user_id, crd):
    crd_old = file_read_user_data(user_id)
    crd_old = crd_old.get(user_id)
    if os.access(file, os.W_OK):
        for line in fileinput.input(file, inplace=True):
            if f"{user_id}:{crd_old[0]}-{crd_old[1]}-{crd_old[2]}" in line:
                line = line.replace(f"{user_id}:{crd_old[0]}-{crd_old[1]}-{crd_old[2]}",
                                    f"{user_id}:{crd[0]}-{crd[1]}-{crd[2]}")
            sys.stdout.write(line)


def file_read_user_data(user_id):
    if os.access(file, os.R_OK):
        with open(file) as text:
            for line in text:
                if str(user_id) in line:
                    key, value = line.split(":")
                    key = int(key)
                    value = value.split("-")
                    value[0] = int(value[0])
                    value[1] = int(value[1])
                    value[2] = int(value[2].replace("\n", ""))
                    data = {key: value}
                    return data


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
