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

PANTRY, PERISHABLE, PHOTO, FEEDBACK = range(4)


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Block D', 'Block E']]

    update.message.reply_text(
        'Hi! My name is RVRC Famyshd.'
        'Which pantry did you put your unopened food in?'
        'Send /cancel to stop the sharing.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return PANTRY


def pantry(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Perishable', 'Non-perishable']]

    user = update.message.from_user
    pantry = update.message.text
    logger.info("%s initiate the food sharing at %s pantry.", user.first_name, pantry)
    update.message.reply_text(
        'Noted.',
        reply_markup=ReplyKeyboardRemove(),
    )
    update.message.reply_text(
        'Is the food perishable or non-perishable?'
        'Send /cancel to stop the sharing.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return PERISHABLE


def perishable(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    perishable = update.message.text
    logger.info("The food shared is %s.", perishable)
    update.message.reply_text(
        'Noted.',
        reply_markup=ReplyKeyboardRemove(),
    )
    update.message.reply_text(
        'Please send me a photo of the food you want to share.'
        'Send /cancel to stop the sharing.\n\n'
    )

    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Lastly, do you have anything to tell us?'
        'or send /skip if you don\'t have anything to say.',
    )

    return FEEDBACK


def feedback(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    feedback = update.message.text
    logger.info(
        "%s\'s feedback: %s", user.first_name, feedback
    )
    update.message.reply_text(
        'Thank you very much for your feedback! Please share food again some day.'
    )

    return ConversationHandler.END


def skip_feedback(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a feedback.", user.first_name)
    update.message.reply_text(
        'Thank you. Please share food again some day.'
    )

    return ConversationHandler.END


'''
def help(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'This is a bot to encourage food sharing culture in RVRC.\n'
        'You can share your unopened food here.\n\n'
        '/start - Start sharing food.\n'
        '/help - View instructions.'
    )


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
'''


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
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PANTRY: [MessageHandler(Filters.regex('^(Block D|Block E)$'), pantry)],
            PERISHABLE: [MessageHandler(Filters.regex('^(Perishable|Non-perishable)$'), perishable)],
            PHOTO: [MessageHandler(Filters.photo, photo)],
            FEEDBACK: [
                MessageHandler(Filters.text & ~Filters.command, feedback),
                CommandHandler('skip', skip_feedback),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(CommandHandler('help', help))
    # dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
