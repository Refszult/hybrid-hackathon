from telebot import types
import datetime
from datetime import datetime, timedelta

from handlers import get_parc_user, get_random_user


def generate_buttons(telegram_id):
    user = get_random_user(telegram_id)
    keyboard = types.InlineKeyboardMarkup()
    if user is not None:
        parc_user = get_parc_user(telegram_id)
        if parc_user is False or parc_user is None:
            key_accept = types.InlineKeyboardButton(text='OK', callback_data='yes')
            keyboard.add(key_accept)
        key_new_date = types.InlineKeyboardButton(
            text='Перенети на ' + str((datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M')),
            callback_data='new_date')
        keyboard.add(key_new_date)
        key_decline = types.InlineKeyboardButton(text='Можно ещё посмтореть?', callback_data='no')
        keyboard.add(key_decline)
    return keyboard
