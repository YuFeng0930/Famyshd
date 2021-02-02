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

GENDER, PHOTO, LOCATION, BIO = range(4)


def transaction(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Hi! My name is RVRC Famyshd.'
    )
    pantry = location()
    perishable = perishable()
    photo()
    

    return GENDER


def location():
    reply_keyboard = [['Block D', 'Block E']]

    update.message.reply_text(
        'Which pantry did you put your unopened food in?'
        'Send /cancel to stop the conversation.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    user = update.message.from_user
    pantry = update.message.text
    logger.info("%s initiate the food sharing at %s pantry.", user.first_name, pantry)
    return pantry


def perishable():
    reply_keyboard = [['Perishable', 'Non-perishable']]

    update.message.reply_text(
        'Is the food perishable or non-perishable?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    user = update.message.from_user
    perishable = update.message.text
    logger.info("The food shared is %s.", perishable)
    return perishable


def photo():
    update.message.reply_text(
        'I see! Please send me a photo of the food you want to share.',
        reply_markup=ReplyKeyboardRemove(),
    )
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Thank you!'
    )

'''
def photo():
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, ' 'or send /skip if you don\'t want to.'
    )

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Maybe I can visit you sometime! ' 'At last, tell me something about yourself.'
    )

    return BIO


def skip_location(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'You seem a bit paranoid! ' 'At last, tell me something about yourself.'
    )

    return BIO


def bio(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END
'''


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! Please share food again some day.', reply_markup=ReplyKeyboardRemove()
    )


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(token='1584429947:AAFbqqLDtWIHu_AEzVVB7c3tTAga7Gnor4c', use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    dispatcher.add_handler(CommandHandler("start", transaction))
    dispatcher.add_handler(CommandHandler("cancel", cancel))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
