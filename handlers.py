import configparser
import os
from datetime import datetime, timedelta

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def connect():
    configs_path = "./"
    config = configparser.ConfigParser()
    config.read(os.path.join(configs_path, "config.ini"))
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user=config.get("db", "user"),
                                      password=config.get("db", "password"),
                                      host=config.get("db", "host"),
                                      port=config.get("db", "port"))
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Курсор для выполнения операций с базой данных
        return connection.cursor()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)


def get_user(telegram_id):
    cursor = connect()
    cursor.execute(f"SELECT * from users where telegram_id = {telegram_id}")
    user = cursor.fetchone()
    print(user)
    cursor.close()
    return user


def create_user(data):
    user = get_user(data.id)
    if user:
        return 'Ты уже зарегестрирован. Для поиска встречи напиши /meeting'
    # TODO: try catch!!!!
    cursor = connect()
    cursor.execute(f"INSERT INTO users (firstname, lastname, telegram_id)"
                   f" VALUES ('{data.first_name}', '{data.last_name}', {data.id})")
    cursor.close()
    return 'Отлично! Зафиксируй еще свою должность. Напиши /position название_должности'


def add_position(telegram_id, position):
    user = get_user(telegram_id)
    cursor = connect()
    if user == []:
        return 'Ты еще не зарегестрирован. Введи команду /start'
    if len(position) > 100:
        return 'Слишком длинное название должности!!!!'
    cursor.execute(f"UPDATE users SET position = '{position}'WHERE telegram_id = {telegram_id}")
    cursor.close()
    return 'Отлично! Регистрация полностью пройдена. Для поиска встречи напиши /meeting'


def create_meeting(telegram_id):
    user = get_user(telegram_id)
    if user is None:
        return 'Ты еще не зарегестрирован. Введи команду /start'
    cursor = connect()
    cursor.execute(f"SELECT * from users where telegram_id != {telegram_id} ORDER BY random() LIMIT 1")
    random_user = cursor.fetchone()
    if random_user is None:
        return False, \
               ['Похоже ты единственный пользователь в системе. Я не могу тебе позволить встретиться с самим собой...'], \
               None
    meet_date = datetime.now() + timedelta(days=2)
    meet_date = meet_date.replace(hour=13, minute=00, second=00)
    cursor.execute(f"INSERT INTO meets (status, start_date, first_user, second_user)"
                   f" VALUES ('PROPOSED', '{meet_date}', {user[0]}, {random_user[0]})")
    meet_date = meet_date.strftime('%Y-%m-%d %H:%M')
    return True, [f'Предлагаем встречу с {random_user[1]} {random_user[2]} - {random_user[3]} в {meet_date}',
                  f'Предлагаем встречу с {user[1]} {user[2]} - {user[3]} в {meet_date}'], \
           random_user[5]


def meeting_reminder(remind):
    print("Ищу")
    cursor = connect()
    cursor.execute(
        f"SELECT * FROM meets WHERE status = 'ACCEPTED' AND start_date BETWEEN (NOW()::date + INTERVAL '1 DAY') AND (NOW()::date + INTERVAL '2 DAY')")
    meets = cursor.fetchall()

    print("Нашёл " + str(len(meets)) + " встреч")

    for meet in meets:
        cursor.execute(
            f"select u.telegram_id, u.firstname, u.lastname from meets_meeting_participants left join meeting_participants mp on mp.id = meets_meeting_participants.participant_id left join users u on u.id = mp.user_id WHERE meet_id = '{meet[3]}'")
        users = cursor.fetchall()

        first_user = users[0]
        second_user = users[1]

        remind(meeting_participant=str(first_user[1] + " " + first_user[2]), user_id=second_user[0])
        remind(meeting_participant=str(second_user[1] + " " + second_user[2]), user_id=first_user[0])
        # remind(meeting_participant="asdfgh", user_id=first_user[4])
