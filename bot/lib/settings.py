"""
This file store token for initialize Telegram Bot
This token you can get in @BotFather.
Also in this file you can setup settings for work with bot.
"""
import os

TOKEN = os.getenv("OTP_CHECK_TOKEN")
BOT_NAME = 'kks_checker_bot'
BOT_URL = f'https://t.me/{BOT_NAME}?start='

# REFRESH TIME FOR UPDATING QR CODE
REFRESH_TIME = 15

# WEB-SERVER PORT
PORT = 8080