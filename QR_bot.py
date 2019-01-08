# pip install telegram
# pip install python-telegram-bot
# pip install pyqrcode
# pip install pypng

TOKEN = 'Your Token'

import logging
import datetime
import os

import pyqrcode
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    ConversationHandler, CallbackQueryHandler

# -----------------------------------------------------------------------------
logging.basicConfig(format='%(asctime)s\n\t%(name)s\n\t%(levelname)s\n\t'
                           '%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants -------------------------------------------------------------------
GO_CreateQR, GO_ReadQR = range(2)

# Messages --------------------------------------------------------------------
msg1 = 'به ربات ساخت کد کیو-آر خوش آمدید'
msg2 = 'لطفا متن خود را وارد کنید:' + '\n\n' +\
       'برای لغو عملیات از دستور زیر استفاده کنید.' + '\n' +\
       '/cancel'
msg3 = 'این کد کد کیو-آر شما میباشد.' \
       ' برای انتقال پول از این کد کیو-آر استفاده خواهد شد' \
       ' لذا آن را در دستگاه خود ذخیره کنید.'

# Buttons ---------------------------------------------------------------------
btn0 = '/Home'
btn1 = '/CreateQR'
btn2 = '/About'
btn3 = '/GiveMyQR'


# ********************************************************* start *************
def start(bot, update):
    uid = update.effective_user.id
    reply_keyboard = [[btn1], [btn2], [btn3]]
    reply_markup = telegram.ReplyKeyboardMarkup(reply_keyboard,
                                                one_time_keyboard=True)
    bot.send_message(chat_id=uid, text=msg1, reply_markup=reply_markup)

    return ConversationHandler.END


# ********************************************************* get_qr_info *******
def get_qr_info(bot, update):
    """receive data from user to create QR"""
    uid = update.effective_user.id
    bot.send_message(chat_id=uid, text=msg2)

    return GO_CreateQR


# ********************************************************* create_qr *********
def create_qr(bot, update):
    """create qr code and sent it to user"""
    uid = update.effective_user.id
    qr_info = update.message.text
    scale = 10

    # creates qr and saves it
    qr = pyqrcode.create(qr_info)
    qr.png('QR/QR_{}.png'.format(uid), scale=scale)

    reply_keyboard = [[btn3], [btn0]]
    reply_markup = telegram.ReplyKeyboardMarkup(reply_keyboard,
                                                one_time_keyboard=True)
    bot.send_message(chat_id=uid,
                     text='تصویر کیو-آر شما با موفقیت ساخته شد!',
                     reply_markup=reply_markup)

    return ConversationHandler.END


# ********************************************************* send_qr ***********
def send_qr(bot, update):
    """send qr_pic"""
    uid = update.effective_user.id

    exists = os.path.isfile('QR/QR_{}.png'.format(uid))
    if exists:
        # read qr pic and send it to user
        qr_pic = open('QR/QR_{}.png'.format(uid), 'rb')
        bot.send_photo(chat_id=uid, photo=qr_pic)

        # show kb
        reply_keyboard = [[btn0]]
        reply_markup = telegram.ReplyKeyboardMarkup(reply_keyboard,
                                                    one_time_keyboard=True)
        bot.send_message(chat_id=uid, text=msg3, reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=uid,
                         text='شما تصویر کیو-آر ندارید!')

    return ConversationHandler.END


# ********************************************************* about *************
def about(bot, update):
    """about function"""
    uid = update.effective_user.id

    keyboard = [[InlineKeyboardButton("پیج اینستاگرام Phika",
                                      url='https://instagram.com/Phika.ir')]]
    reply_keyboard = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=uid,
                     text='Our Instagram Page',
                     reply_keyboard=reply_keyboard)

    return ConversationHandler.END


# ********************************************************* cancel ************
def cancel(bot, update):
    """cancel function"""
    reply_keyboard = [[btn0]]
    reply_markup = telegram.ReplyKeyboardMarkup(reply_keyboard,
                                                one_time_keyboard=True)
    bot.send_message(chat_id=update.effective_user.id,
                     text='شما عملیات را با موفقیت لغو کردید!' + '\n\n' +
                          'برای برگشت به منو اصلی'
                          ' میتوانید از دکمه Home استفاده کنید.',
                     reply_markup=reply_markup)
    return ConversationHandler.END


# ********************************************************* error *************
def error(update, error_):
    """Log Errors caused by Updates."""
    logger.warning('Update "{}" caused error "{}"'.format(update, error_))


# ********************************************************* main **************
def main():
    """main function"""
    updater = Updater(TOKEN) #Phikabot
    dp = updater.dispatcher

    updater.dispatcher.add_handler(CallbackQueryHandler(cancel))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler('home', start),
                      CommandHandler('CreateQR', get_qr_info),
                      CommandHandler('GiveMyQR', send_qr),
                      CommandHandler('About', about)],
        states={
            GO_CreateQR: [MessageHandler(Filters.text, create_qr)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
