# Подключаем модуль случайных чисел
import datetime
from datetime import datetime, timedelta

import threading
import time
import schedule

# Подключаем модуль для Телеграма
import telebot
from telebot import types

from handlers import get_user, create_user, add_position, create_meeting, change_meeting_date, approved_meeting, \
    declined_meeting, meeting_reminder, set_rating

with open("token", "r") as f:
    token = f.read()
    print(token)
#
# # Указываем токен
bot = telebot.TeleBot(token)


# Метод, который получает сообщения и обрабатывает их
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши /start")
    elif message.text.find("/position") != -1:
        response = add_position(message.from_user.id, message.text.replace('/position', ''))
        bot.send_message(message.from_user.id, response)
    elif message.text == "/start":
        user = get_user(message.from_user.id)
        if user:
            if user[3]:
                bot.send_message(message.from_user.id, "Для поиска встречи напиши /meeting.")
            else:
                bot.send_message(message.from_user.id, "Зафиксируй свою должность. Напиши /position название_должности")
        else:
            response = create_user(message.from_user)
            bot.send_message(message.from_user.id, response)
    elif message.text == "/meeting":
        response_status, response, second_user_id = create_meeting(message.from_user.id)

        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        key_accept = types.InlineKeyboardButton(text='OK', callback_data='yes')  # кнопка «Да»
        keyboard.add(key_accept)  # добавляем кнопку в клавиатуру
        key_new_date = types.InlineKeyboardButton(
            text='Перенети на ' + str((datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M')),
            callback_data='new_date')  # кнопка «Да»
        keyboard.add(key_new_date)  # добавляем кнопку в клавиатуру
        key_decline = types.InlineKeyboardButton(text='Можно ещё посмтореть?', callback_data='no')
        keyboard.add(key_decline)
        # question = 'Тебе '+str(age)+' лет, тебя зовут '+name+' '+surname+'?'
        # bot.send_message(message.from_user.id, text="встреча!", reply_markup=keyboard)

        if response_status:
            bot.send_message(second_user_id, response[1], reply_markup=keyboard)
        bot.send_message(message.from_user.id, response[0], reply_markup=keyboard)
    elif message.text == "/vote":
        msg = "Как прошла ваша встреча? Ваше мнение важно для нас. Выберите картинку:"

        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        keyboard.add(types.InlineKeyboardButton(text='🤩', callback_data='2'))
        keyboard.add(types.InlineKeyboardButton(text='😎', callback_data='1'))
        keyboard.add(types.InlineKeyboardButton(text='🤨', callback_data='0'))
        keyboard.add(types.InlineKeyboardButton(text='😬', callback_data='-1'))
        keyboard.add(types.InlineKeyboardButton(text='🤮', callback_data='-2'))

        bot.send_message(message.from_user.id, msg, reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


def remind(meeting_participant, user_id):
    msg = "Напоминаем: у вас встреча с " + meeting_participant + "в " + str((datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M'))
    bot.send_message(user_id, msg)

def job():
    print("Запускаю поиск встреч для напоминания")
    meeting_reminder(remind)

schedule.every(2).seconds.do(job)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        response = approved_meeting(call.message.chat.id, True, bot)
        bot.send_message(call.message.chat.id, response)
    elif call.data == "no":
        response_status, response, users = declined_meeting(call.message.chat.id)
        if response_status:
            bot.send_message(users[0], response)
            bot.send_message(users[1], response)
        else:
            bot.send_message(call.message.chat.id, response)
    elif call.data == "new_date":
        status_response, response, users = change_meeting_date(call.message.chat.id)
        if status_response:
            bot.send_message(users[0], response)
            bot.send_message(users[1], response)
        else:
            bot.send_message(call.message.chat.id, response)
    elif call.data in ["-2", "-1", "0", "1", "2"]:
        msg = set_rating(call.message.chat.id, call.data)
        bot.send_message(call.message.chat.id, msg)

def worker():
    # нужно иметь свой цикл для запуска планировщика с периодом в 1 секунду:
    while True:
        schedule.run_pending()
        time.sleep(1)

t = threading.Thread(target=worker, args=())

t.start()
# Запускаем постоянный опрос бота в Телеграме
b = threading.Thread(target=bot.polling(none_stop=True, interval=0), args=())
b.start()





