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

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

PANTRY_START, PERISHABLE_START, PHOTO_START, PANTRY_UPDATE, PHOTO_UPDATE, FEEDBACK_START, FEEDBACK_UPDATE = range(7)


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Block D', 'Block E']]

    update.message.reply_text(
        'Hi! My name is RVRC Famyshd.'
        'Which pantry did you put your unopened food in? '
        'Send /cancel to stop the sharing.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return PANTRY_START


def pantry_start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Perishable', 'Non-perishable']]

    user = update.message.from_user
    pantry = update.message.text
    logger.info("%s initiate the food sharing at %s pantry.", user.first_name, pantry)
    update.message.reply_text(
        'Noted.',
        reply_markup=ReplyKeyboardRemove(),
    )
    update.message.reply_text(
        'Is the food perishable or non-perishable? '
        'Send /cancel to stop the sharing.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return PERISHABLE_START


def perishable_start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    perishable = update.message.text
    logger.info("The food shared is %s.", perishable)
    update.message.reply_text(
        'Noted.',
        reply_markup=ReplyKeyboardRemove(),
    )
    update.message.reply_text(
        'Please send me a photo of the food you want to share. '
        'Send /cancel to stop the sharing.\n\n'
    )

    return PHOTO_START


def photo_start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Lastly, do you have anything to tell us? '
        'or send /skip if you don\'t have anything to say.',
    )

    return FEEDBACK_START


def feedback_start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    feedback = update.message.text
    logger.info(
        "%s\'s feedback: %s", user.first_name, feedback
    )
    update.message.reply_text(
        'Thank you very much for your feedback! Please share food again some day.'
    )

    return ConversationHandler.END


def skip_feedback_start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a feedback.", user.first_name)
    update.message.reply_text(
        'Thank you. Please share food again some day.'
    )

    return ConversationHandler.END


def status(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Block D', 'Block E']]

    update.message.reply_text(
        'Hi! My name is RVRC Famyshd.'
        'Which pantry did you take the food from? '
        'Send /cancel to stop the updating.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return PANTRY_UPDATE


def pantry_update(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    pantry = update.message.text
    logger.info("%s update the food sharing at %s pantry.", user.first_name, pantry)
    update.message.reply_text(
        'Noted.',
        reply_markup=ReplyKeyboardRemove(),
    )
    update.message.reply_text(
        'Please send me a photo of the food after you take. '
        'Send /cancel to stop the sharing.\n\n'
    )

    return PHOTO_UPDATE


def photo_update(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Lastly, do you have anything to tell us? '
        'or send /skip if you don\'t have anything to say.',
    )

    return FEEDBACK_UPDATE


def feedback_update(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    feedback = update.message.text
    logger.info(
        "%s\'s feedback: %s", user.first_name, feedback
    )
    update.message.reply_text(
        'Thank you very much for your feedback! Please also share food some day.'
    )

    return ConversationHandler.END


def skip_feedback_update(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a feedback.", user.first_name)
    update.message.reply_text(
        'Thank you. Please also share food some day.'
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
    updater = Updater('1584429947:AAFbqqLDtWIHu_AEzVVB7c3tTAga7Gnor4c')

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler_start = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PANTRY_START: [MessageHandler(Filters.regex('^(Block D|Block E)$'), pantry_start)],
            PERISHABLE_START: [MessageHandler(Filters.regex('^(Perishable|Non-perishable)$'), perishable_start)],
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

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
