import threading
import time
import schedule

# Подключаем модуль для Телеграма
import telebot
from telebot import types
from telegram import ParseMode

from buttons import generate_buttons, generate_position_buttons
from handlers import get_user, create_user, add_position, create_meeting, change_meeting_date, approved_meeting, \
    declined_meeting, meeting_reminder, set_rating, get_history, get_rating_history, vote_reminder

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
        bot.send_message(message.from_user.id, "Напиши /start для работы с ботом \n"
                                               "/history - для получение информации по последним 10 встречам \n"
                                               "/rating - для получения текущего рейтинга")
    elif message.text.find("/position") != -1:
        response_status, response = add_position(message.from_user.id, message.text.replace('/position', ''))
        bot.send_message(message.from_user.id, response)
        if response_status:
            meeting(message.from_user.id)
    elif message.text == "/start":
        user = get_user(message.from_user.id)
        if user:
            if user[3]:
                bot.send_message(message.from_user.id, "Для поиска встречи напиши /meeting.")
            else:
                bot.send_message(message.from_user.id, "Зафиксируй свою должность. Напиши /position название_должности",
                                 reply_markup=generate_position_buttons())
        else:
            response = create_user(message.from_user)
            bot.send_message(message.from_user.id, response, reply_markup=generate_position_buttons())
    elif message.text == "/meeting":
        meeting(message.from_user.id)
    elif message.text == "/vote":
        msg = "Как прошла ваша встреча? Ваше мнение важно для нас. Выберите картинку:"

        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        keyboard.add(types.InlineKeyboardButton(text='🤩', callback_data='2'))
        keyboard.add(types.InlineKeyboardButton(text='😎', callback_data='1'))
        keyboard.add(types.InlineKeyboardButton(text='🤨', callback_data='0'))
        keyboard.add(types.InlineKeyboardButton(text='😬', callback_data='-1'))
        keyboard.add(types.InlineKeyboardButton(text='🤮', callback_data='-2'))

        bot.send_message(message.from_user.id, msg, reply_markup=keyboard)
    elif message.text == "/history":
         table = get_history(message.from_user.id)
         bot.send_message(message.from_user.id, f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
    elif message.text == "/rating":
        response = get_rating_history(message.from_user.id)
        if response > 0:
            emoji = '😎'
        else:
            emoji = '👹'
        bot.send_message(message.from_user.id, f'Твой рейтинг {response} {emoji}')
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /start.")


def remind(meeting_participant, user_id, date):
    msg = "Напоминаем: у вас встреча с " + meeting_participant + "в " + str(date.strftime('%Y-%m-%d %H:%M'))
    bot.send_message(user_id, msg)


def job():
    print("Запускаю поиск встреч для напоминания")
    meeting_reminder(remind)


schedule.every(60).seconds.do(job)


def remind_vote(user_id):
    bot.send_message(user_id, "Оцени свою прошедшую встречу, введи команду /vote")


def job_vote():
    print("Запускаю поиск встреч для напоминания о необходимости оценить встречу")
    vote_reminder(remind_vote)


schedule.every().day.at("13:30").do(job_vote)
#schedule.every(60).seconds.do(job_vote)


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
    elif call.data in ["HR", "Manager", "Developer"]:
        response_status, response = add_position(call.message.chat.id, call.data)
        bot.send_message(call.message.chat.id, response)
        if response_status:
            meeting(call.message.chat.id)


def worker():
    # нужно иметь свой цикл для запуска планировщика с периодом в 1 секунду:
    while True:
        schedule.run_pending()
        time.sleep(1)


def meeting(id):
    response_status, response, second_user_id = create_meeting(id)
    keyboard = generate_buttons(id)
    if response_status:
        bot.send_message(second_user_id, response[1], reply_markup=keyboard)
    bot.send_message(id, response[0], reply_markup=keyboard)

t = threading.Thread(target=worker, args=())

t.start()
# Запускаем постоянный опрос бота в Телеграме
b = threading.Thread(target=bot.polling(none_stop=True, interval=0), args=())
b.start()





