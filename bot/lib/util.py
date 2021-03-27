import hashlib
from os import urandom
from random import choice

from loguru import logger

# Telegram stuff
from telegram import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    KeyboardButton, 
    ReplyKeyboardMarkup, 
    Update
)

from telegram.ext import (
    CallbackContext, 
    CallbackQueryHandler,
    ConversationHandler
)

from lib.remote_server import RemoteServer
from lib.settings import *


# State definitions for top level conversation
REGISTRATION, LOCATION, CHECK = map(chr, range(3))
# State definitions for registration conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# State definition for otp verification
CHECK_OTP = chr(20)

# Meta state
STOPPING = map(chr, range(4, 5))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Differents states
(
    MAIN_REG,
    REGISTRATION_USER,
    CHECK_USER,
    START_OVER,
    CURRENT_FEATURE,
) = map(chr, range(10, 15))

# Global variable for checking otp_code and verification
otp_code = hashlib.md5(urandom(32)).hexdigest()

# Init class RemoteServer for work with remote server
r_server = RemoteServer()

# Some basic function
def mumble(update: Update, cx: CallbackContext):
    """If user not choice available options send 'i don't know' message"""

    stickers = [
        'CAACAgIAAxkBAAINAl-9nTmXosBfTTsgxqkLPzuoxWWMAAIoAQACzk6PArBGaMYEVWBEHgQ',
        'CAACAgIAAxkBAAINFF-9nlokjHN1b9ugRAGt6XkcO5t7AAIUAQACzk6PArThej9_OS8VHgQ'
    ]

    sticker = choice(stickers)
    update.message.reply_sticker(sticker)


def send_dev(update: Update, cx: CallbackContext):
    """If user choose /dev than send message about developer"""

    text =  "Если вы заметили какие-то сбои в программе, "
    text += "то сообщите разработчику: @delvinru -- Алексей\n"
    text += "Формат сообщения:\n"
    text += "Issue: *Проблема*\n"
    text += "Описание проблемы (можно приложить скриншот)."

    update.message.reply_text(text=text, parse_mode="Markdown")


def send_help(update: Update, cx: CallbackContext):
    text =  "Используй /start, чтобы начать взаимодействовать с ботом\n"
    text += "Если у вас возникли проблемы, пропишите команду /stop.\n"
    text += "Если и это не помогло, обратитесь к преподавателю."
    update.message.reply_text(text)


def stop(update: Update, cx: CallbackContext) -> int:
    update.message.reply_text(text='Хорошо, может по новой?')
    return END


def start(update: Update, cx: CallbackContext):
    """Initialize main window"""

    # Check user was init or not
    if cx.user_data.get(START_OVER):
        text = f'Привет, {cx.user_data["login"]}!\n'

        # Sometimes this code got exception because message don't callback query
        try:
            update.callback_query.answer()
            update.callback_query.edit_message_text(text=text)
        except:
            update.message.reply_text(text)

        try:
            data = update.message.text
        except:
            # if OTP-code not provided in /start than just end conversation or other shit
            return END

        code = data.removeprefix('/start ')
        if code != '/start':
            check_otp_code(update, cx, code)

        return END
    else:
        user_id = update.message.from_user.id
        cx.user_data["uid"] = user_id

        new_user = False
        cached_user = ''

        if not cx.user_data.get('login'):
            user = r_server.search_user(user_id)
            if user is None:
                new_user = True
            else:
                cached_user = user 
        
        if cached_user != '':
            cx.user_data['login'] = cached_user

        # If new user was detected
        if new_user:
            keyboard = [
                [InlineKeyboardButton('Зарегистрироваться', callback_data=str(REGISTRATION_USER))],
            ]
            text =  "Привет, это бот для учёта посещаемости студентов на парах.\n"
            text += "Вводите логин, который вы указываете на сайте https://git.bk252.ru/.\n"
            text += "Если вы опечатались, то данные можно поправить до нажатия кнопки 'Завершить регистрацию'\n"
            text += "❗️❗️❗\n️Будьте внимательны, после её нажатия изменить свои данные нельзя.\nОбращайтесь к преподавателю.\n❗️❗️❗️"
            text += "\n"
            text += "Для того, чтобы отметиться на паре тебе достаточно отсканировать QR-код, который покажет преподаватель на доске."
            text += "Чтобы пройти регистрацию нажмите на кнопку ниже👇\n"

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                text,
                reply_markup=reply_markup
            )

            logger.info(f'New user {user_id} came to registration menu.')

            return REGISTRATION
        else:
            text = f'Привет, {cx.user_data["login"]}!\n'

            update.message.reply_text(text=text)

            try:
                data = update.message.text
            except:
                # if code not provided in /start than just end conversation
                return END

            code = data.removeprefix('/start ')
            if code != '/start':
                check_otp_code(update, cx, code)

            return END

###
# Functions that are required for user registration
###
def reg_select_feature(update: Update, cx: CallbackContext) -> str:
    """Main menu of registration field"""
    buttons = [
        [
            InlineKeyboardButton('Логин', callback_data='login')
        ],
        [
            InlineKeyboardButton('Введённые данные', callback_data='show_data'),
            InlineKeyboardButton('Завершить регистрацию', callback_data='done')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    text = 'Нажми на кнопку, чтобы указать свои данные.'
    if not cx.user_data.get(START_OVER):
        # First run of this function
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    return SELECTING_FEATURE


def show_data(update: Update, cx: CallbackContext):
    """Show info about user in registration field"""

    cx.user_data[CURRENT_FEATURE] = update.callback_query.data

    text = "*Твой профиль*\n"

    if cx.user_data.get('login'):
        text += f'*Логин:* {cx.user_data["login"]}\n'
    else:
        text += f'*Логин:* пока не указан\n'

    buttons = [[InlineKeyboardButton(text='Назад', callback_data='back')]]
    keyboard = InlineKeyboardMarkup(buttons)

    cx.user_data[START_OVER] = False
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=text, 
        reply_markup=keyboard, 
        parse_mode='Markdown'
    )

    return MAIN_REG


def ask_for_input(update: Update, cx: CallbackContext):
    """Prompt for user input"""

    cx.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Хорошо, жду информацию🙄'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    return TYPING


def save_input(update: Update, cx: CallbackContext):
    """Save user state in context"""

    cx.user_data['uid'] = update.message.from_user.id
    cx.user_data['username'] = update.message.from_user.username

    current_option = cx.user_data[CURRENT_FEATURE]
    user_text = update.message.text

    bad_input = False

    if current_option == 'login':
        if len(user_text) == 0:
            bad_input = True
        else:
            cx.user_data['login'] = user_text

    if bad_input:
        cx.bot.send_message(
            chat_id=update.message.chat.id,
            text='Вы ввели какие-то некорректные данные.🤔\nПопробуйте снова'
        )

    cx.user_data[START_OVER] = True
    return reg_select_feature(update, cx)


@logger.catch
def register_user(update: Update, cx: CallbackContext):
    """Add user to database"""

    # If tried register without name or group show data and start again
    if not cx.user_data.get('login'):
        logger.error(f'User {cx.user_data["uid"]} try register without required field')
        cx.user_data[START_OVER] = True
        return show_data(update, cx)

    # Init user on server
    res = r_server.init_user(
        cx.user_data['uid'],
        cx.user_data['login']
    )

    if not res:
        update.callback_query.answer()
        update.callback_query.edit_message_text(text='Извини, но я не могу опознать тебя на сервере🤔\nПопробуй снова отправив /start')
        cx.user_data.pop('login')
        cx.user_data.pop(START_OVER)
        return END

    logger.info(f'User {cx.user_data["uid"]} {cx.user_data["username"]} was registered')

    cx.user_data[START_OVER] = True
    start(update, cx)
    return END


def stop_reg(update: Update, cx: CallbackContext):
    """End registration"""
    update.message.reply_text('Хорошо, пока!')
    return END

###
# Functions that are needed to mark the user
###
def stop_check(update: Update, cx: CallbackContext):
    """End of check"""
    update.message.reply_text('Хорошо, пока!')
    return END


def check_otp_code(update: Update, cx: CallbackContext, code: str):
    """Functions check OTP code input by user and if correct mark him in DB"""

    # Count failed tries
    if not cx.user_data.get('otp_try'):
        cx.user_data['otp_try'] = 0

    global otp_code
    if code == otp_code:
        # mark user in database
        res = r_server.mark_user(cx.user_data['uid'])

        if not res:
            cx.bot.send_message(
                chat_id=update.message.chat.id,
                text='Упс, кажется, ты где-то накосячил! Я не смог тебя отметить на паре😉'
            )
            return END

        logger.info(
            f'{cx.user_data["uid"]} {cx.user_data["login"]} was marked on server'
        )

        # send successfull message
        cx.bot.send_message(
            chat_id=update.message.chat.id,
            text='Поздравляю, ты отмечен на паре!☺️'
        )

        return END
    else:
        cx.user_data['otp_try'] += 1

        if cx.user_data['otp_try'] >= 3:
            logger.error(
                f'{cx.user_data["uid"]} {cx.user_data["login"]} entered the password incorrectly more than 3 times.'
            )
        else:
            logger.warning(
                f'{cx.user_data["uid"]} {cx.user_data["login"]} try incorrect password'
            )

        bad_messages = [
            'Друг, а ты точно на паре?👿',
            'Самая быстрая рука на диком западе? Точно нет😉',
            'Короче, Меченый, я тебя спас и в благородство играть не буду: отметишься на паре — и мы в расчете.'
        ]

        cx.bot.send_message(
            chat_id=update.message.chat.id,
            text=choice(bad_messages)
        )

        return END