"""
This file store token for initialize Telegram Bot
This token you can get in @BotFather.
"""
import os

TOKEN = os.getenv("TOKEN_CHECKER_OS")
BOT_NAME = 'kks_checker_bot'
BOT_URL = f'https://t.me/{BOT_NAME}?start='

# REFRESH TIME FOR UPDATING QR CODE
REFRESH_TIME = 13