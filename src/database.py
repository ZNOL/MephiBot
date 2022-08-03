import asyncio
import pymysql
from src.bot import *
from pytz import timezone
from datetime import datetime, timedelta, time


def commit_execute(sql, values=None):
    with pymysql.connect(
            # host=DB_HOST,
            unix_socket=DB_SOCKET,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,

    ) as con:
        with con.cursor() as cursor:
            try:
                cursor.execute(sql, values)
                con.commit()
                logging.info(f'OK: {sql}')
            except Exception as e:
                logging.error(str(e))


def fetchone_execute(sql, values=None):
    with pymysql.connect(
            # host=DB_HOST,
            unix_socket=DB_SOCKET,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
    ) as con:
        with con.cursor() as cursor:
            try:
                cursor.execute(sql, values)
                logging.info(f'OK: {sql}')
                return cursor.fetchone()
            except Exception as e:
                logging.error(str(e))
                return ()


def fetchall_execute(sql, values=None):
    with pymysql.connect(
            # host=DB_HOST,
            unix_socket=DB_SOCKET,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
    ) as con:
        with con.cursor() as cursor:
            try:
                cursor.execute(sql, values)
                logging.info(f'OK: {sql}')
                return cursor.fetchall()
            except Exception as e:
                logging.error(str(e))
                return ()


def on_start(createBase=False, createTable=False, showTable=False):
    if createBase:
        sql = f'CREATE DATABASE {DB_DATABASE}'
        with pymysql.connect(
                # host=DB_HOST,
                unix_socket=DB_SOCKET,
                user=DB_USER,
                password=DB_PASSWORD,
                cursorclass=pymysql.cursors.DictCursor
        ) as con:
            with con.cursor() as cursor:
                cursor.execute(sql)
                con.commit()
    if createTable:
        drop_devices_query = 'DROP TABLE IF EXISTS `users`'
        create_devices_query = '''
                CREATE TABLE `users` (
                    `id` bigint NOT NULL PRIMARY KEY,
                    `is_controller` int NOT NULL,
                    `is_admin` int NOT NULL,
                    `button_id` int DEFAULT 0,
                    `name` varchar(60) DEFAULT 'Нет данных',
                    `likes` int DEFAULT 0,
                    `current_group` text DEFAULT NULL,
                    `is_active` int DEFAULT 0
                );
                '''
        drop_buttons_query = 'DROP TABLE IF EXISTS `buttons`'
        create_buttons_query = """
                CREATE TABLE `buttons` (
                    `id` int NOT NULL PRIMARY KEY,
                    `value` text NOT NULL,
                    `prev_id` int NOT NULL,
                    `next_count` int NOT NULL
                );
                """
        with pymysql.connect(
                # host=DB_HOST,
                unix_socket=DB_SOCKET,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                cursorclass=pymysql.cursors.DictCursor
        ) as con:
            with con.cursor() as cursor:
                cursor.execute(drop_devices_query)
                cursor.execute(drop_buttons_query)
                con.commit()
                cursor.execute(create_devices_query)
                cursor.execute(create_buttons_query)
                con.commit()
    if showTable:
        show_devises_query = 'DESCRIBE users'
        show_buttons_query = 'DESCRIBE buttons'
        with pymysql.connect(
                # host=DB_HOST,
                unix_socket=DB_SOCKET,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                cursorclass=pymysql.cursors.DictCursor
        ) as con:
            with con.cursor() as cursor:
                cursor.execute(show_devises_query)
                result = cursor.fetchall()
                print(*result, sep='\n')
                print()
                cursor.execute(show_buttons_query)
                result = cursor.fetchall()
                print(*result, sep='\n')


def get_next_id(tableName):
    sql = f"SELECT MAX(id) FROM {tableName}"
    result = fetchone_execute(sql)['MAX(id)']
    if result is None:
        return 1
    else:
        return result + 1


def update(id, filed, value, table):
    sql = f"UPDATE `{table}` SET {filed} = %s WHERE id = %s"
    commit_execute(sql, (value, id))


def users_add(id, is_controller=0, is_admin=0):
    sql = f"INSERT INTO users (id, is_controller, is_admin) VALUES (%s, %s, %s)"
    commit_execute(sql, (id, is_controller, is_admin))


def users_delete(id):
    sql = f"DELETE FROM users WHERE id = %s"
    commit_execute(sql, (id, ))


def users_is_controller(id):
    sql = f"SELECT is_controller FROM users WHERE id = %s"
    try:
        return bool(fetchone_execute(sql, (id, ))["is_controller"])
    except TypeError:
        return False


def users_is_admin(id):
    sql = f"SELECT is_admin FROM users WHERE id = %s"
    try:
        return bool(fetchone_execute(sql, (id, ))["is_admin"])
    except TypeError:
        return False


def users_get(id):
    sql = f"SELECT * FROM users WHERE id = %s"
    return fetchone_execute(sql, (id, ))


def users_get_all():
    sql = f"SELECT * FROM users"
    return fetchall_execute(sql)


def buttons_add(value, prev_id, next_count=0):
    sql = f"INSERT INTO buttons (id, value, prev_id, next_count) "\
          f"VALUES (%s, %s, %s, %s)"
    new_id = get_next_id('buttons')
    commit_execute(sql, (new_id, value, prev_id, next_count))
    return new_id


def buttons_delete(id, onlyOne=False):
    sql = f"DELETE FROM buttons WHERE id = %s"

    buttonInfo = buttons_get(id=id)
    if buttonInfo["prev_id"] > 0:
        new_count = buttons_get(id=buttonInfo["prev_id"])["next_count"]
        new_count = new_count - 1 if new_count - 1 >= 0 else 0
        update(buttonInfo["prev_id"], 'next_count', new_count, 'buttons')

    if not onlyOne:
        for value in buttons_get_all(id):
            buttons_delete(value["id"])

    commit_execute(sql, (id, ))


def buttons_get(id=None, value=None):
    sql = f"SELECT * FROM buttons WHERE "
    if id is not None:
        sql += "id = %s"
        values = (id, )
    else:
        sql += "value = %s"
        values = (value, )
    return fetchone_execute(sql, values)


def buttons_get_all(prev_id=None):
    sql = f"SELECT * FROM buttons"
    values = None
    if prev_id is not None:
        sql += f" WHERE prev_id = %s"
        values = (prev_id, )
    return fetchall_execute(sql, values)


try:
    connection = pymysql.connect(
        # host=DB_HOST,
        unix_socket=DB_SOCKET,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )

    on_start(showTable=True)

    logging.info('BASE CONNECTED')
except Exception as e:
    print(str(e))
    # on_start(createBase=True, createTable=True, showTable=True)
    logging.error(str(e))
