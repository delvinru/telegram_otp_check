"""
This file store token for initialize Telegram Bot
This token you can get in @BotFather.
Also in this file you can setup settings for work with bot.
"""
import os

TOKEN = os.getenv('OTP_CHECK_TOKEN')

BOT_NAME = os.getenv('BOT_NAME')
BOT_URL = f'https://t.me/{BOT_NAME}?start='

REMOTE_SERVER = os.getenv('REMOTE_SERVER') 
REMOTE_SERVER_LOGIN = os.getenv('LOGIN')
REMOTE_SERVER_PASSWORD = os.getenv('PASSWORD')

# REFRESH TIME FOR UPDATING QR CODE
REFRESH_TIME = 15