import configparser
import os
from datetime import datetime, timedelta
import prettytable as pt

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
    cursor.close()
    return user


def get_user_by_id(id):
    cursor = connect()
    cursor.execute(f"SELECT telegram_id from users where id = {id}")
    user = cursor.fetchone()
    cursor.close()
    return user[0]


def get_user_fulldata_by_id(id):
    cursor = connect()
    cursor.execute(f"SELECT * from users where id = {id}")
    user = cursor.fetchone()
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
        return False, 'Ты еще не зарегестрирован. Введи команду /start'
    if len(position) > 100:
        return False, 'Слишком длинное название должности!!!!'
    if len(position) == 0:
        position = 'Сотрудник'
    cursor.execute(f"UPDATE users SET position = '{position}'WHERE telegram_id = {telegram_id}")
    cursor.close()
    return True, 'Отлично! Регистрация полностью пройдена.'


def create_meeting(telegram_id):
    user = get_user(telegram_id)
    if user is None:
        return False, ['Ты еще не зарегестрирован. Введи команду /start'], None
    cursor = connect()
    cursor.execute(f"SELECT * from meets where (first_user = {user[0]} or second_user = {user[0]}) "
                   f"and status != 'DONE' and status != 'DECLINED' ORDER BY id DESC LIMIT 1")
    meet = cursor.fetchone()
    cursor.close()
    if meet is not None:
        return False, ['У тебя уже есть запланированная встреча. Если она тебя не устраивает, то отмени ее.'], None
    random_user = get_random_user(telegram_id)
    cursor = connect()
    if random_user is None:
        return False, \
               ['Похоже ты единственный пользователь в системе. Я не могу тебе позволить встретиться с самим собой...'], \
               None
    meet_date = datetime.now() + timedelta(days=2)
    meet_date = meet_date.replace(hour=13, minute=00, second=00)
    cursor.execute(f"INSERT INTO meeting_participants (is_accept, user_id)"
                   f" VALUES (false, {user[0]}) RETURNING id")
    meet_first_user_id = cursor.fetchone()
    cursor.execute(f"INSERT INTO meeting_participants (is_accept, user_id)"
                   f" VALUES (false, {random_user[0]}) RETURNING id")
    meet_second_user_id = cursor.fetchone()
    cursor.execute(f"INSERT INTO meets (status, start_date, first_user, second_user)"
                   f" VALUES ('PROPOSED', '{meet_date}', {user[0]}, {random_user[0]}) RETURNING id")
    meet_id = cursor.fetchone()
    cursor.execute(f"INSERT INTO meets_meeting_participants (meet_id, participant_id)"
                   f" VALUES ({meet_id[0]}, {meet_first_user_id[0]})")
    cursor.execute(f"INSERT INTO meets_meeting_participants (meet_id, participant_id)"
                   f" VALUES ('{meet_id[0]}', {meet_second_user_id[0]})")
    meet_date = meet_date.strftime('%Y-%m-%d %H:%M')
    cursor.close()
    return True, [f'Предлагаем встречу с {random_user[1]} {random_user[2]} - {random_user[3]} в {meet_date}',
                  f'Предлагаем встречу с {user[1]} {user[2]} - {user[3]} в {meet_date}'], \
           random_user[5]


def meeting_reminder(remind):
    cursor = connect()
    cursor.execute(
        f"SELECT * FROM meets WHERE status = 'ACCEPTED' AND notified is null AND start_date BETWEEN (NOW()::date + INTERVAL '1 DAY') AND (NOW()::date + INTERVAL '2 DAY')")
    meets = cursor.fetchall()

    print("Нашёл " + str(len(meets)) + " встреч")

    for meet in meets:
        cursor.execute(
            f"select u.telegram_id, u.firstname, u.lastname from meets_meeting_participants left join meeting_participants mp on mp.id = meets_meeting_participants.participant_id left join users u on u.id = mp.user_id WHERE meet_id = '{meet[3]}'")
        users = cursor.fetchall()

        first_user = users[0]
        second_user = users[1]

        remind(meeting_participant=str(first_user[1] + " " + first_user[2]), user_id=second_user[0], date=meet[1])
        remind(meeting_participant=str(second_user[1] + " " + second_user[2]), user_id=first_user[0], date=meet[1])

        cursor.execute(f"UPDATE meets SET notified = 'true' WHERE id = '{meet[3]}'")

    cursor.close()


def approved_meeting(telegram_id, approved_status, bot):
    user = get_user(telegram_id)
    if user is None:
        return 'Ты еще не зарегестрирован. Введи команду /start'
    cursor = connect()
    cursor.execute(f"SELECT id from meeting_participants where user_id = {user[0]} ORDER BY id DESC LIMIT 1")
    meeting_participants_id = cursor.fetchone()
    cursor.execute(
        f"UPDATE meeting_participants SET is_accept = '{approved_status}'WHERE id = {meeting_participants_id[0]}")
    check_meet(bot, cursor, user[0])
    cursor.close()
    return 'Отлично! Ты подтвердил встречу!'


def change_meeting_date(telegram_id):
    user = get_user(telegram_id)
    if user is None:
        return False, 'Ты еще не зарегестрирован. Введи команду /start', None
    cursor = connect()
    cursor.execute(f"SELECT * from meets where first_user = {user[0]} or second_user = {user[0]} ORDER BY id DESC LIMIT 1")
    meeting = cursor.fetchone()
    if meeting is None:
        return False, 'Встреча не найдена. Введи команду /meeting', None
    meet_date = meeting[1] + timedelta(days=1)
    telegram_id_first = get_user_by_id(meeting[2])
    telegram_id_second = get_user_by_id(meeting[4])
    cursor.execute(f"UPDATE meets SET start_date = '{meet_date}'WHERE id = {meeting[3]}")
    return True, 'Встреча перенесена на один день.', \
           [telegram_id_first, telegram_id_second]


def check_meet(bot, cursor, user_id):
    cursor.execute(f"SELECT first_user, second_user, start_date, id from meets where first_user = {user_id}"
                   f" or second_user = {user_id} ORDER BY id DESC LIMIT 1")
    meet_parc = cursor.fetchone()
    cursor.execute(f"SELECT is_accept from meeting_participants where user_id = {meet_parc[0]} ORDER BY id DESC LIMIT 1")
    first_parc = cursor.fetchone()
    cursor.execute(f"SELECT is_accept from meeting_participants where user_id = {meet_parc[1]} ORDER BY id DESC LIMIT 1")
    second_parc = cursor.fetchone()
    if first_parc[0] and second_parc[0]:
        cursor.execute(f"UPDATE meets SET status = 'ACCEPTED' WHERE id = {meet_parc[3]}")
        message = f"Оба участника подтвердили встречу! Встреча состоится в {meet_parc[2].strftime('%Y-%m-%d %H:%M')}"
        first_user_telegram = get_user_by_id(meet_parc[0])
        second_user_telegram = get_user_by_id(meet_parc[1])
        bot.send_message(first_user_telegram, message)
        bot.send_message(second_user_telegram, message)


def declined_meeting(telegram_id):
    user = get_user(telegram_id)
    if user is None:
        return False, 'Ты еще не зарегестрирован. Введи команду /start', None
    cursor = connect()
    cursor.execute(f"SELECT first_user, second_user, id from meets where first_user = {user[0]}"
                   f" or second_user = {user[0]} ORDER BY id DESC LIMIT 1")
    meet = cursor.fetchone()
    cursor.execute(f"UPDATE meets SET status = 'DECLINED' where id = {meet[2]}")
    first_user_telegram = get_user_by_id(meet[0])
    second_user_telegram = get_user_by_id(meet[1])
    cursor.close()
    return True, 'Твоя встреча отменена! Напиши /meeting для формирования новой встречи.', \
           [first_user_telegram, second_user_telegram]


def set_rating(id, rating):
    cursor = connect()
    cursor.execute(f"UPDATE meeting_participants SET rating = '{rating}' WHERE id in (select mp.id from meets left join meets_meeting_participants mmp on meets.id = mmp.meet_id left join meeting_participants mp on mp.id = mmp.participant_id left join users u on u.id = mp.user_id where status = 'ACCEPTED' and u.telegram_id <> '{id}')")
    cursor.close()
    return "Сбасибо, Ваш голос засчитан"
    
def get_parc_user(telegram_id):
    user = get_user(telegram_id)
    if user is None:
        return False, 'Ты еще не зарегестрирован. Введи команду /start', None
    cursor = connect()
    cursor.execute(f"SELECT is_accept from meeting_participants where user_id = {user[0]} ORDER BY id DESC LIMIT 1")
    is_accept = cursor.fetchone()
    if is_accept is None:
        return False
    return is_accept[0]


def get_random_user(telegram_id):
    cursor = connect()
    exist = cursor.execute("SELECT * FROM meets limit 1")
    cursor.fetchone()
    if exist is not None:
        cursor.execute(f"SELECT * from users"
                       f" LEFT JOIN meets ON users.id = meets.first_user OR users.id = meets.second_user"
                       f" where telegram_id != {telegram_id}"
                       f" AND meets.status != 'PROPOSED'"
                       f" AND meets.status != 'PARTIALLY_ACCEPTED'"
                       f" AND meets.status != 'ACCEPTED'"
                       f" AND meets.status != 'IN_PROGRESS'"
                       f" AND meets.status != 'WAIT_FOR_RATE'"
                       f" ORDER BY random() LIMIT 1")
    else:
        cursor.execute(f"SELECT * from users"
                       f" where telegram_id != {telegram_id}"
                       f" ORDER BY random() LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    return result


def get_history(telegram_id):
    user = get_user(telegram_id)
    if user is None:
        return False, 'Ты еще не зарегестрирован. Введи команду /start', None
    cursor = connect()
    cursor.execute(f"SELECT * from meets where (first_user = {user[0]} or second_user = {user[0]})"
                   f" and status = 'DONE'"
                   f" ORDER BY id DESC"
                   f" LIMIT 10")
    history = cursor.fetchall()
    table = pt.PrettyTable(['Участник', 'Еще один участник', 'Дата встречи'])
    for elem in history:
        first_user = get_user_fulldata_by_id(elem[2])
        second_user = get_user_fulldata_by_id(elem[4])
        table.add_row([f"{first_user[1]} {first_user[2]} - {first_user[3]}",
                      f"{second_user[1]} {second_user[2]} - {second_user[3]}",
                       elem[1].strftime('%Y-%m-%d %H:%M')])
    return table


def get_rating_history(telegram_id):
    user = get_user(telegram_id)
    if user is None:
        return False, 'Ты еще не зарегестрирован. Введи команду /start', None
    cursor = connect()
    cursor.execute(f"SELECT SUM(rating) FROM meeting_participants WHERE user_id = {user[0]}")
    rating = cursor.fetchone()
    cursor.close()
    return rating[0]




