# -*- coding: utf-8 -*-
import os
import re
from telegram import ParseMode
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
import datetime
from logs import logger
from stats_logger import StatsLogger
import requests
import json
import random
import string
# t.me/fastqr_bot
token ='1761862188:AAFBDCXd8M6VomcbzRrdYa5jhVeHFV8EVQI'
admin_id = '1669591481' #Your telegram id

def au(update,context,admin_id):
     update.message.reply_text(f'Hello @{update.effective_user.username}')


stats_logger = StatsLogger('stats.json')

#regex for match text to qr
regex_url = "^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$"

start_msg = '🤍Hi!!💚\n\nWelcome to Zakura!!!\n\n✅ Premium User  ✅You can use this bot'
error_msg_photo = 'Для создания qr-кода с картинкой в фоне необходимо прислать в одном сообщении картинку с описанием (в описании картинки просто впиши ссылку)'
owner_msg = 'MY OWNER IS @JUANPZT'
def make_qrfile(text, photo = None):
    filename = datetime.datetime.utcnow().strftime('img/%Y%m%d_%H%M%S.%f')[:-3] + '.png'

    # https://github.com/sylnsfar/qrcode
    run_string = f'myqr {text} -n {filename}' if photo is None else f'myqr {text} -n {filename} -p {photo} -c -con 1.2'
    os.system(run_string)

    return filename

def start(update, context):
    user = update.message.from_user
    stats_logger.new_request(user)
    logger.info(f"{user.first_name} has started bot")
    update.message.reply_photo(photo=open('logo.jpg', 'rb'), caption = start_msg, parse_mode=ParseMode.MARKDOWN)
    

def stats(update, context):
    user = update.message.from_user

    #allow access only to You
    if user.id == admin_id:
        users, stats_data = stats_logger.get_top()

        return_string = f'**Total Users {users}**\n\n**Active Clicks:**'
        for day in stats_data:
            return_string += f'\n`{day[0]}` - {day[1]}'

        update.message.reply_text(text = return_string, parse_mode=ParseMode.MARKDOWN)

def gates(update, context):
   update.message.reply_text(f'Hello @{update.effective_user.username}')

def makeqr_photo(update, context):
    global regex_url
    user = update.message.from_user
    text = update.message.caption.lower()
    stats_logger.new_request(user)
    os.popen("/usr/bin/influx -username admin -password 'strongpassword123QWE' -database 'wg' -execute 'INSERT bots,botname=fastqr,actiontype=message action=true'")

    #check antiflood message length and match regex filter
    if text and len(text) < 400 and re.match(regex_url, text):
        logger.info(f"User {user.first_name} has sended photo with caption {text}")

        #download photo
        photo_file = update.message.photo[-1].get_file()
        photo_name = datetime.datetime.utcnow().strftime('covers/%Y%m%d_%H%M%S.%f')[:-3]+ '.jpg'
        photo_file.download(photo_name)

        #make qr with photo
        qr_filename = make_qrfile(text, photo_name)

        #send qr image
        update.message.reply_photo(photo=open(qr_filename, 'rb'))
    else:
        replytext = f'{error_msg_photo}\n\n{error_msg}'
        update.message.reply_text(replytext, parse_mode=ParseMode.MARKDOWN)

def makeqr_text(update, context):
    user = update.message.from_user
    text = update.message.text.lower()
    stats_logger.new_request(user)
    os.popen("/usr/bin/influx -username admin -password 'strongpassword123QWE' -database 'wg' -execute 'INSERT bots,botname=fastqr,actiontype=message action=true'")

    #check antiflood message length and match regex filter
    if text and len(text) < 400 and re.match(regex_url, text):
        logger.info(f"User {user.first_name} has sended text {text}")

        #make qr
        qr_filename = make_qrfile(text)

        #send qr image
        update.message.reply_photo(photo=open(qr_filename, 'rb'))
    else:
        logger.info(f"User {user.first_name} has sended wrong text {'none' if text is None else text}")
        update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    logger.info(f"Application started")

    # create folders
    if not os.path.exists('img'):
        os.makedirs('img')
        logger.info(f"Created dir /img")

    if not os.path.exists('covers'):
        os.makedirs('covers')
        logger.info(f"Created dir /covers")

    #setup telegram bot
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # message handlers
    dp.add_handler(CommandHandler("gates", gates))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(MessageHandler(Filters.text, makeqr_text))
    dp.add_handler(MessageHandler(Filters.photo, makeqr_photo))

    # log all errors
    dp.add_error_handler(error)

    logger.info(f"EL BOT INICIO")

    
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
