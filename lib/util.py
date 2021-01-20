# Telegram stuff
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext
)

from lib.dbhelper import DBHelper
from re import findall
from datetime import datetime
from time import time
from loguru import logger
from random import choice


# State definitions for top level conversation
REGISTRATION, LOCATION, CHECK = map(chr, range(3))
# State definitions for registration conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))

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

# Init class DBhelper for work with db
db = DBHelper()

# Some basic function


def mumble(update: Update, cx: CallbackContext) -> None:
    """If user not choice available options send 'i don't know' message"""

    stickers = [
        'CAACAgIAAxkBAAINAl-9nTmXosBfTTsgxqkLPzuoxWWMAAIoAQACzk6PArBGaMYEVWBEHgQ',
        'CAACAgIAAxkBAAINFF-9nlokjHN1b9ugRAGt6XkcO5t7AAIUAQACzk6PArThej9_OS8VHgQ'
    ]
    sticker = choice(stickers)
    update.message.reply_sticker(sticker)


def send_dev(update: Update, cx: CallbackContext) -> None:
    """If user choose /dev than send message about developer"""

    text = 'Если вы заметили какие-то сбои в моей программе, \
    то сообщите моему создателю: @delvinru -- Алексей'
    update.message.reply_text(text=text)


def send_help(update: Update, cx: CallbackContext) -> None:
    update.message.reply_text(
        text='Используй /start, чтобы начать взаимодействовать с ботом')


def stop(update: Update, cx: CallbackContext) -> None:
    update.message.reply_text(text='Хорошо, пока!')
    return END


def start(update: Update, cx: CallbackContext) -> None:
    """Initialize main window"""

    # Check user was init or not
    if cx.user_data.get(START_OVER):
        text = f'Привет, {cx.user_data["name"]}!\n'
        text += 'Ты можешь отметиться на паре!'
        buttons = [[
            InlineKeyboardButton(
                'Отметиться на паре', 
                callback_data=str(CHECK_USER)
            )
        ]]
        keyboard = InlineKeyboardMarkup(buttons)

        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text, reply_markup=keyboard)

        return CHECK
    else:
        user_id = update.message.from_user.id
        user = db.search_user(user_id)

        # If new user was detected
        if user is None:
            keyboard = [
                [InlineKeyboardButton(
                    'Зарегистрироваться', callback_data=str(REGISTRATION_USER))],
            ]
            text = 'Привет, это бот для учёта посещаемости студентов на парах.\n'
            text += "Чтобы начать регистрацию нажмите на кнопку ниже👇\n"
            text += "Вводите полное ФИО. Если вы опечатались, то данные можно поправить до нажатия кнопки 'Завершить регистрацию'\n"
            text += "❗️❗️❗\n️Будьте внимательны, после её нажатия изменить свои данные нельзя.\nОбращайтесь к преподавателю или к разработчику.\n❗️❗️❗️"

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                text,
                reply_markup=reply_markup
            )

            cx.user_data["uid"] = user_id
            return REGISTRATION
        else:
            # user = (id, name)
            text = f'Привет, {user[1]}!\n'
            text += 'Ты можешь отметиться на паре!'
            buttons = [[
                InlineKeyboardButton(
                    'Отметиться на паре', 
                    callback_data=str(CHECK_USER)
                )
            ]]
            keyboard = InlineKeyboardMarkup(buttons)
            update.message.reply_text(text=text, reply_markup=keyboard)

            # Put info in context menu
            cx.user_data['uid'] = user[0]
            cx.user_data['name'] = user[1]

            logger.info(f'User {user[0]} {user[1]} come to me')

            return CHECK

###
# Functions that are required for user registration
###
def reg_select_feature(update: Update, cx: CallbackContext) -> None:
    """Main menu of registration field"""
    buttons = [
        [
            InlineKeyboardButton('ФИО', callback_data='name'),
            InlineKeyboardButton('Группа', callback_data='group')
        ],
        [
            InlineKeyboardButton(
                'Введённые данные',
                callback_data='show_data'),
            InlineKeyboardButton('Завершить регистрацию', callback_data='done')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    text = 'Нажми на кнопку, чтобы указать свои данные.'
    if not cx.user_data.get(START_OVER):
        # First run of this function
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    return SELECTING_FEATURE


def show_data(update: Update, cx: CallbackContext) -> None:
    """Show info about user in registration field"""

    cx.user_data[CURRENT_FEATURE] = update.callback_query.data

    text = "*Твой профиль*\n"
    if cx.user_data.get('name'):
        text += f'*ФИО:* {cx.user_data["name"]}\n'
    else:
        text += f'*ФИО:* пока не указано\n'

    if cx.user_data.get('group'):
        text += f'*Группа:* {cx.user_data["group"]}\n'
    else:
        text += f'*Группа:* пока не указана\n'

    buttons = [[InlineKeyboardButton(text='Назад', callback_data='back')]]
    keyboard = InlineKeyboardMarkup(buttons)

    cx.user_data[START_OVER] = False
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=text, reply_markup=keyboard, parse_mode='Markdown')

    return MAIN_REG


def ask_for_input(update: Update, cx: CallbackContext) -> None:
    """Prompt for user input"""

    cx.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Хорошо, жду информацию🙄'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    return TYPING


def save_input(update: Update, cx: CallbackContext) -> None:
    """Save user state in context"""

    cx.user_data['uid'] = update.message.from_user.id
    cx.user_data['username'] = update.message.from_user.username
    current_option = cx.user_data[CURRENT_FEATURE]
    user_text = update.message.text

    regex_group = r'^\S{4}-\d{2}-\d{2}$'
    regex_name = r'\S{3,} \S{3,} \S{3,}'

    bad_input = False
    if current_option == 'name':
        if len(findall(regex_name, user_text)) > 0:
            cx.user_data['name'] = update.message.text
        else:
            bad_input = True
    elif current_option == 'group':
        if len(findall(regex_group, user_text)) > 0:
            cx.user_data['group'] = update.message.text.upper()
        else:
            bad_input = True

    if bad_input:
        cx.bot.send_message(
            chat_id=update.message.chat.id,
            text='Вы ввели какие-то некорректные данные.🤔\nПопробуйте снова')

    cx.user_data[START_OVER] = True
    return reg_select_feature(update, cx)


@logger.catch
def register_user(update: Update, cx: CallbackContext) -> None:
    """Add user to database"""

    # If tried register without name or group show data and start again
    if not cx.user_data.get('name') or not cx.user_data.get('group'):
        logger.error(
            f'User {cx.user_data["uid"]} try register without required field')
        cx.user_data[START_OVER] = True
        return show_data(update, cx)

    if not cx.user_data.get('username'):
        logger.warning(f'User {cx.user_data["name"]} with empty username')
        cx.user_data['username'] = 'None'

    # Create user in database
    db.init_user(
        cx.user_data['uid'],
        cx.user_data['username'],
        cx.user_data['name'],
        cx.user_data['group'])

    logger.info(
        f'User {cx.user_data["uid"]} {cx.user_data["username"]} was registered')

    cx.user_data[START_OVER] = True
    start(update, cx)
    return END


def stop_reg(update: Update, cx: CallbackContext) -> None:
    """End registration"""
    update.message.reply_text('Хорошо, пока!')
    return END

###
# Functions that are needed to mark the user
###
def stop_check(update: Update, cx: CallbackContext) -> None:
    """End of check"""
    update.message.reply_text('Хорошо, пока!')
    return END


def check_user(update: Update, cx: CallbackContext) -> None:
    """Check is user exist in database"""

    db.mark_user(cx.user_data['uid'])
    logger.info(
        f'{cx.user_data["uid"]} {cx.user_data["name"]} was marked in DB')
    update.callback_query.edit_message_text(text='Поздравляю, ты на паре!☺️')

    return END
