import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def connect():
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user='postgres',
                                      password='1448',
                                      host='localhost',
                                      port='5432')
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
    return 'Отлично! Регистрация полностью пройдена. Для поиска встречи напиши /meeting'

