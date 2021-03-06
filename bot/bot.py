# Others import
import sys
from threading import Thread
import subprocess

# Imports for telegram API
import telegram
from loguru import logger
from telegram import Update
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

# My libs
from lib.dbhelper import DBHelper
from lib.settings import *
from lib.util import *
from lib.rest_api import *
from lib.otp_generator import *


def main():
    """Initialize all logic for work"""
    # setup DBHelper
    db = DBHelper()
    db.setup()

    # Telegram setting
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    start_reg = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                reg_select_feature,
                pattern='^' + str(REGISTRATION_USER) + '$'
            )
        ],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(ask_for_input, pattern='^(name|group).*$'),
                CallbackQueryHandler(show_data, pattern='^show_data$')
            ],
            TYPING: [
                MessageHandler(Filters.text & ~Filters.command, save_input)
            ],
            MAIN_REG: [
                CallbackQueryHandler(reg_select_feature, pattern='^back$')
            ]
        },
        fallbacks=[
            CallbackQueryHandler(register_user, pattern='^done$'),
            CommandHandler('stop', stop_reg)
        ],
        map_to_parent={
            END: STOPPING
        },
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REGISTRATION: [start_reg],
            CHECK_OTP: [MessageHandler(Filters.text & ~Filters.command, check_otp_code)],
            STOPPING: [CommandHandler('start', start)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)

    # Handlers for command
    dp.add_handler(CommandHandler('help', send_help))
    dp.add_handler(CommandHandler('dev', send_dev))

    # Handlers for mumble
    dp.add_handler(
        MessageHandler( (Filters.text | Filters.sticker) & (~Filters.command), mumble) 
    )

    # Start OTP code generator
    otp_generator = Thread(target=generate_otp)
    otp_generator.start()

    # Start websocket server
    websocket_thread = Thread(target=start_websocket)
    websocket_thread.start()

    # Start long polling
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    # Set base logging
    logger.remove()
    logger.add(
        "logs/debug.log",
        format="[{time:YYYY-MM-DD HH:mm:ss}] {level} | {message}",
        level="DEBUG",
        rotation="1 MB")
    logger.add(sys.__stdout__)

    if TOKEN is None:
        logger.error("export TOKEN_CHECKER_OS in environment")
        exit(0)

    main()
