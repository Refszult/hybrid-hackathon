# Подключаем модуль случайных чисел
import datetime
import random
from datetime import datetime, timedelta

# Подключаем модуль для Телеграма
import telebot
from telebot import types

from handlers import get_user, create_user, add_position, create_meeting

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

        keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
        key_accept = types.InlineKeyboardButton(text='OK', callback_data='yes'); # кнопка «Да»
        keyboard.add(key_accept); # добавляем кнопку в клавиатуру
        key_new_date = types.InlineKeyboardButton(text='Перенети на ' + str((datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M')), callback_data='new_date'); # кнопка «Да»
        keyboard.add(key_new_date); # добавляем кнопку в клавиатуру
        key_decline= types.InlineKeyboardButton(text='Можно ещё посмтореть?', callback_data='no');
        keyboard.add(key_decline);
        # question = 'Тебе '+str(age)+' лет, тебя зовут '+name+' '+surname+'?';
        # bot.send_message(message.from_user.id, text="встреча!", reply_markup=keyboard)

        if response_status:

            bot.send_message(second_user_id, response[1], reply_markup=keyboard)
        bot.send_message(message.from_user.id, response[0], reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # Если нажали на одну из 12 кнопок — выводим гороскоп
    if call.data == "zodiac":
        # Формируем гороскоп
        msg = random.choice(first) + ' ' + random.choice(second) + ' ' + random.choice(
            second_add) + ' ' + random.choice(third)
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)


# Запускаем постоянный опрос бота в Телеграме
bot.polling(none_stop=True, interval=0)
