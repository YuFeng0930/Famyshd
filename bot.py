#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import datetime

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)


import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

PORT = int(os.environ.get('PORT', 5000))
TOKEN = '1504384034:AAGrRYIBUQ8bb0SqQgKZP0ZsXQA15rxG0gk'
global storage
storage = {}

logger = logging.getLogger(__name__)

PANTRY_START, PERISHABLE_START, BOX_START, PHOTO_START, FEEDBACK_START, PANTRY_UPDATE, PERISHABLE_UPDATE, BOX_UPDATE, PHOTO_UPDATE, FEEDBACK_UPDATE = range(10)


class FoodInfo:
    def __init__(self, pantry):
        self.pantry = pantry
    
    def put_perishable(self, perishable):
        self.perishable = perishable

    def put_box(self, box):
        self.box = box

    def put_time_clear(self, time_clear):
        self.time_clear = time_clear

    def put_photo_name(self, photo_name):
        self.photo_name = photo_name

def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Block D', 'Block E']]
    update.message.reply_text(
        'Hello! Welcome to Famyshd, RVRC’s very own food sharing service. '
        'Which pantry did you put your upopened food in? '
        'Send /cancel to stop sharing.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return PANTRY_START


def pantry_start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Perishable', 'Non-perishable']]

    user = update.message.from_user
    chat_id = update.message.chat.id
    pantry = update.message.text

    logger.info("%s initiate the food sharing at %s pantry.", user.first_name, pantry)
    update.message.reply_text(
        'Got it.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    # Update the storage
    storage[chat_id] = FoodInfo(pantry)

    update.message.reply_text(
        'Is the food perishable or non-perishable? '
        'Send /cancel to stop sharing.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return PERISHABLE_START


def perishable_start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat.id
    perishable = update.message.text

    logger.info("The food shared is %s.", perishable)
    update.message.reply_text(
        'Got it.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    # Update the storage
    food_info = storage.get(chat_id)
    food_info.put_perishable(perishable)
    storage[chat_id] = food_info
    pantry = food_info.pantry[-1]

    reply_keyboard = [[pantry + '1', pantry + '2', pantry + '3', pantry + '4']]
    update.message.reply_text(
        'Which box did you put your upopened food in? '
        'Send /cancel to stop sharing.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return BOX_START


def box_start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat.id
    box = update.message.text

    logger.info("The food is put in box %s.", box)
    update.message.reply_text(
        'Got it.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    # Update the storage
    food_info = storage.get(chat_id)
    food_info.put_box(box)
    storage[chat_id] = food_info

    update.message.reply_text(
        'Please send me a photo of the food you want to share. '
        'Send /cancel to stop sharing.\n\n'
    )

    return PHOTO_START


def photo_start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat.id
    photo_file = update.message.photo[-1].get_file()
    time = datetime.datetime.now()
    time_clear = datetime.datetime.now() + datetime.timedelta(hours=9)
    photo_name = 'share-' + str(time) + '.jpg'
    update.message.reply_text(
        'A moment please...\n\n'
    )

    # Update the storage
    food_info = storage.get(chat_id)
    food_info.put_photo_name(photo_name)
    food_info.put_time_clear(time_clear)
    storage[chat_id] = food_info

    photo_file.download(photo_name)
    logger.info("Photo of %s: %s", user.first_name, photo_name)
    update.message.reply_text(
        'Great! Lastly, do you have any additional comments about the food '
        '(i.e non-halal, freshness etc.) or the station? '
        'Send /skip if you don\'t have anything to say.\n\n',
    )

    return FEEDBACK_START


def feedback_start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat.id
    feedback = update.message.text

    food_info = storage.pop(chat_id)

    message = 'Location: ' + str(food_info.pantry) + ' pantry\n'     
    message += 'Box: ' + str(food_info.box) + '\n' 
    message += 'Food type: ' + str(food_info.perishable) + ' food\n'
    if food_info.perishable == 'Perishable':
        message += '(The food will be cleared up by %02d:%02d)\n' % (food_info.time_clear.hour, food_info.time_clear.minute)
    message += '(Remarks: %s)\n' % (feedback)
    # context.bot.send_photo(chat_id=926113388, photo=open(photo_name_start, 'rb')) # send to YuFeng personal chat
    # context.bot.send_message(chat_id=926113388, text=message)
    context.bot.send_photo(chat_id=-1001477409473, photo=open(food_info.photo_name, 'rb')) # send to Try Channel
    context.bot.send_message(chat_id=-1001477409473, text=message)

    logger.info(
        "%s\'s feedback: %s", user.first_name, feedback
    )
    update.message.reply_text(
        'Thank you for sharing some of your food! '
        'I’m sure someone would appreciate it! Cheers!\n\n'
    )

    return ConversationHandler.END


def skip_feedback_start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat.id

    food_info = storage.pop(chat_id)

    message = 'Location: ' + str(food_info.pantry) + ' pantry\n' 
    message += 'Box: ' + str(food_info.box) + '\n' 
    message += 'Food type: ' + str(food_info.perishable) + ' food\n'
    if food_info.perishable == 'Perishable':
        message += '(The food will be cleared up by %02d:%02d)\n' % (food_info.time_clear.hour, food_info.time_clear.minute)
    # context.bot.send_photo(chat_id=926113388, photo=open(photo_name_start, 'rb')) # send to YuFeng personal chat
    # context.bot.send_message(chat_id=926113388, text=message)
    context.bot.send_photo(chat_id=-1001477409473, photo=open(food_info.photo_name, 'rb')) # send to Try Channel
    context.bot.send_message(chat_id=-1001477409473, text=message)

    logger.info("User %s did not send a feedback.", user.first_name)
    update.message.reply_text(
        'Thank you for sharing some of your food! '
        'I’m sure someone would appreciate it! Cheers!\n\n'
    )

    return ConversationHandler.END


def status(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Block D', 'Block E']]

    update.message.reply_text(
        'Hello! Welcome to Famyshd, RVRC’s very own food sharing service. '
        'Which pantry did you take the food from? '
        'Send /cancel to stop the update.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return PANTRY_UPDATE


def pantry_update(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Perishable', 'Non-perishable']]

    user = update.message.from_user
    chat_id = update.message.chat.id
    pantry = update.message.text

    logger.info("%s update the food sharing at %s pantry.", user.first_name, pantry)
    update.message.reply_text(
        'Got it.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    ## Update the storage
    storage[chat_id] = FoodInfo(pantry)

    update.message.reply_text(
        'Is the food perishable or non-perishable? '
        'Send /cancel to stop the update.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return PERISHABLE_UPDATE


def perishable_update(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat.id
    perishable = update.message.text

    logger.info("The food updated is %s.", perishable)
    update.message.reply_text(
        'Got it.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    # Update the storage
    food_info = storage.get(chat_id)
    food_info.put_perishable(perishable)
    storage[chat_id] = food_info
    pantry = food_info.pantry[-1]


    reply_keyboard = [[pantry + '1', pantry + '2', pantry + '3', pantry + '4']]
    update.message.reply_text(
        'Which box did you take the food from? '
        'Send /cancel to stop updating.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return BOX_UPDATE


def box_update(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat.id
    box = update.message.text

    logger.info("The food is taken from box %s.", box)
    update.message.reply_text(
        'Got it.\n\n',
        reply_markup=ReplyKeyboardRemove(),
    )

    # Update the storage
    food_info = storage.get(chat_id)
    food_info.put_box(box)
    storage[chat_id] = food_info

    update.message.reply_text(
        'Please send me a photo of the food after you have taken it. '
        'Send /cancel to stop the update.\n\n'
    )

    return PHOTO_UPDATE



def photo_update(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat.id
    photo_file = update.message.photo[-1].get_file()
    time = datetime.datetime.now()
    photo_name = 'update-' + str(time) + '.jpg'
    update.message.reply_text(
        'A moment please...\n\n'
    )

    food_info = storage.pop(chat_id)

    photo_file.download(photo_name)
    message = '* Food update *\n' + 'Location: ' + str(food_info.pantry) + ' pantry\n'
    message += 'Box: ' + str(food_info.box) + '\n' 
    # context.bot.send_photo(chat_id=926113388, photo=open(photo_name, 'rb')) # send to YuFeng personal chat
    # context.bot.send_message(chat_id=926113388, message=message)
    context.bot.send_photo(chat_id=-1001477409473, photo=open(photo_name, 'rb')) # send to Try Channel
    context.bot.send_message(chat_id=-1001477409473, text=message)
    logger.info("Photo of %s: %s", user.first_name, photo_name)
    update.message.reply_text(
        'Great! Lastly, do you have anything to tell us? '
        'Send /skip if you don\'t have anything to say.\n\n',
    )

    return FEEDBACK_UPDATE


def feedback_update(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    feedback = update.message.text
    logger.info(
        "%s\'s feedback: %s", user.first_name, feedback
    )
    update.message.reply_text(
        'Thank you and hope you enjoy your food! Cheers!\n\n'
    )
    context.bot.send_message(chat_id=926113388, text=feedback)

    return ConversationHandler.END


def skip_feedback_update(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a feedback.", user.first_name)
    update.message.reply_text(
        'Thank you and hope you enjoy your food! Cheers!\n\n'
    )

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! Please share food again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater('1504384034:AAGrRYIBUQ8bb0SqQgKZP0ZsXQA15rxG0gk')

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler_start = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PANTRY_START: [MessageHandler(Filters.regex('^(Block D|Block E)$'), pantry_start)],
            PERISHABLE_START: [MessageHandler(Filters.regex('^(Perishable|Non-perishable)$'), perishable_start)],
            BOX_START: [MessageHandler(Filters.regex('^(D1|D2|D3|D4|E1|E2|E3|E4)$'), box_start)],
            PHOTO_START: [MessageHandler(Filters.photo, photo_start)],
            FEEDBACK_START: [
                MessageHandler(Filters.text & ~Filters.command, feedback_start),
                CommandHandler('skip', skip_feedback_start),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    conv_handler_update = ConversationHandler(
        entry_points=[CommandHandler('update', status)],
        states={
            PANTRY_UPDATE: [MessageHandler(Filters.regex('^(Block D|Block E)$'), pantry_update)],
            PERISHABLE_UPDATE: [MessageHandler(Filters.regex('^(Perishable|Non-perishable)$'), perishable_update)],
            BOX_UPDATE: [MessageHandler(Filters.regex('^(D1|D2|D3|D4|E1|E2|E3|E4)$'), box_update)],
            PHOTO_UPDATE: [MessageHandler(Filters.photo, photo_update)],
            FEEDBACK_UPDATE: [
                MessageHandler(Filters.text & ~Filters.command, feedback_update),
                CommandHandler('skip', skip_feedback_update),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler_start)
    dispatcher.add_handler(conv_handler_update)

    # updater.start_polling()
    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                        port=int(PORT),
                        url_path=TOKEN)
    updater.bot.setWebhook('https://blooming-everglades-53145.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
