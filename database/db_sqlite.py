import sqlite3

name = f'C:/Users/cooln/PycharmProjects/testFAPI/bot/my_database.db'
# connection = sqlite3.connect(name, check_same_thread=False)
# cursor = connection.cursor()
ind = ['id', 'username', 'worklog_errors', 'doccorp_errors']


def auth(user_id, user_name):
    connection = sqlite3.connect(name, check_same_thread=False)
    cursor = connection.cursor()
    user = cursor.execute(f'SELECT * FROM USERS WHERE ID = {user_id}').fetchone()
    if user is None:
        cursor.execute(f"INSERT INTO USERS VALUES ('{user_id}', '{user_name}', 0, 0)")
        user = (user_id, user_name, 0, 0)
    user = dict(zip(ind, user))
    connection.commit()
    connection.close()
    return user


def update(col_error, new_value, user_id):
    connection = sqlite3.connect(name, check_same_thread=False)
    cursor = connection.cursor()
    update_stmt = f'UPDATE USERS SET {col_error}={new_value} WHERE ID={user_id}'
    cursor.execute(update_stmt)
    connection.commit()
    connection.close()


def select(col_error):
    connection = sqlite3.connect(name, check_same_thread=False)
    cursor = connection.cursor()
    select_stmt = f'SELECT ID FROM USERS WHERE {col_error}=1'
    res = cursor.execute(select_stmt).fetchall()
    connection.close()
    return res
