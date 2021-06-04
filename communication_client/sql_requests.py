import sqlite3
import flask
import secrets
import bcrypt
import datetime as dt
import numpy as np

#PATH when on the VM
data_file='/home/ubuntu/serveur/swypeek_final.db'

#Normal PATH
#data_file='../swypeek_final.db'

def dict_factory(cursor, row):
    """used to turn lists into dictionaries while using sqlite
    because it's more convenient using json"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def add_row(table, data):
    # data is a dictionary where key = column and value = value for this specific (row, column)
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    
    #creating (?, ?, ..., ?) with the right number of question marks to make secure requests
    question_marks="("
    for i in range(len(list(data.values()))-1):
        question_marks+='?, '
    question_marks+='?)'

    cur.execute(
        "INSERT INTO " + table + " (" + ', '.join(data.keys()) + ") VALUES " + question_marks + ";", list(data.values()))
    
    conn.commit()
    conn.close()
    return cur.lastrowid


def existing_user():
    query_parameters = flask.request.args
    conn = sqlite3.connect(data_file)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute('SELECT user_id, username FROM users WHERE email = ?', [query_parameters.get('email')]).fetchall()
    conn.close()
    return flask.jsonify(results)


def check_credentials():
    data = flask.request.form
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()

    #encodes the password in utf-8 ('pythön!' => b'pyth\xc3\xb6n!')
    pwd = data.get('password').encode()
    
    if(data.get('username')==None):
        data_query=[data.get('email'),data.get('email')]
    else:
        data_query=[data.get('username'),data.get('username')]

    results=cur.execute('SELECT user_id, username, expiration_date, password FROM users WHERE (username = ? \
        OR email = ?);', data_query).fetchall()
    
    if(results==[]):
        conn.close()
        return "Wrong username/email"
    #if the given password corresponds to its hash in the database:
    elif(bcrypt.checkpw(pwd, results[0][3].encode())):
        user_id = results[0][0]
        date_obj = dt.datetime.strptime(results[0][2], "%Y-%m-%d")
        new_date = dt.datetime(date_obj.year, (date_obj.month) % 12 +1, date_obj.day)
        expiration_date = dt.datetime.strftime(new_date, "%Y-%m-%d")
        token = int('0x' + str(secrets.token_hex(8)), 16)
        cur.execute('UPDATE users SET token_value = ' + str(token) + ", expiration_date = '" + expiration_date + "' WHERE user_id = ?", [str(user_id)])
        conn.commit()
        conn.close()
        return str(results[0][0])
    else:
        conn.close()
        return "Wrong password"


def check_group_credentials():
    data = flask.request.form
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    
    group_code = data.get('group_code')
    group_name = data.get('group_name')

    results = cur.execute('SELECT group_id FROM groups WHERE group_name = ? AND group_code = ?', [group_name, group_code]).fetchall()

    if(results==[]):
        conn.close()
        return "Wrong group code or group name"
    else:
        conn.close()
        return str(results[0][0])


def update_has_swiped(group_id, user_id, swipe_direction):
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    cur.execute('UPDATE users_groups SET has_swiped = ? WHERE user_id = ? AND group_id = ?', [swipe_direction, user_id, group_id])
    conn.commit()
    results = cur.execute('SELECT has_swiped FROM users_groups WHERE group_id = ?', [group_id]).fetchall()
    conn.close()
    return [i[0] for i in results]


def reset_has_swiped(group_id):
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    cur.execute('UPDATE users_groups SET has_swiped = 0 WHERE group_id = ?', [group_id])
    conn.commit()
    conn.close()


def delete_rows(table, id_name, id_value):
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM ' + table + ' WHERE ' + id_name + '= ?', [id_value])
        conn.commit()
        if cur.rowcount == 0:
            conn.close()
            return 'Failed to delete ' + id_name + ' = ' + id_value + ' from ' + table
    except sqlite3.Error as err:
        conn.close()
        return str(err)
    conn.close()
    return id_name + ' = ' + id_value + ' from ' + table + ' was successfully deleted.'


def getMovieSpec(movie_id):
    conn = sqlite3.connect(data_file)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute('SELECT * FROM movies WHERE movie_id = ?', [movie_id]).fetchall()[0]
    conn.close()
    return results


def getNicknames(group_id):
    L={}
    conn = sqlite3.connect(data_file)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute('SELECT COUNT(nickname) FROM users_groups WHERE group_id = ?', [group_id]).fetchone()
    cpt = results.get('COUNT(nickname)')
    for i in range(cpt):
        nickname = cur.execute('SELECT nickname FROM users_groups WHERE group_id = ?', [group_id]).fetchall()[i].get('nickname')
        L[i]=nickname
    conn.close()
    return L


def getGroupId(group_id):
    conn = sqlite3.connect(data_file)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute('SELECT group_id FROM groups WHERE group_id = ?', [group_id]).fetchall()
    conn.close()
    return flask.jsonify(results)
