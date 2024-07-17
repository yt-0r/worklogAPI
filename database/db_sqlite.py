import sqlite3

connection = sqlite3.connect('my_database.db', check_same_thread=False)
cursor = connection.cursor()
ind = ['id', 'username', 'worklog_errors', 'doccorp_errors']


def auth(user_id, user_name):
    user = cursor.execute(f'SELECT * FROM USERS WHERE ID = {user_id}').fetchone()
    if user is None:
        cursor.execute(f"INSERT INTO USERS VALUES ('{user_id}', '{user_name}', 0, 0)")
        user = (user_id, user_name, 0, 0)
    user = dict(zip(ind, user))
    connection.commit()
    return user


def update(col_error, new_value, user_id):
    update_stmt = f'UPDATE USERS SET {col_error}={new_value} WHERE ID={user_id}'
    connection.execute(update_stmt)
    connection.commit()
