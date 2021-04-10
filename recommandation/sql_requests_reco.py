import sqlite3
import numpy as np

data_file='../swypeek.db'


def importRatings():
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    ratings = cur.execute("SELECT * FROM users_movies;").fetchall()
    conn.close()
    return ratings

def importRating(user, movie):
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    rating = cur.execute("SELECT rating FROM users_movies WHERE user_id = ? AND movie_id = ?;", [user, movie]).fetchall()
    conn.close()
    return rating[0][0]


def maxIdUsers():
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    max_id = cur.execute("SELECT MAX(user_id) FROM users;").fetchall()
    conn.close()
    return max_id[0][0]


def maxIdMovies():
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    max_id = cur.execute("SELECT MAX(movie_id) FROM movies;").fetchall()
    conn.close()
    return max_id[0][0]


def user_list(group_id):
    """
    given the id of a group, returns the list of users in the group
    """
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    user_list=cur.execute("SELECT user_id FROM users_groups WHERE group_id = ?;", [group_id]).fetchall()
    conn.close()
    return [i[0] for i in user_list]


def allUserIds():
    """
    Returns a list with every user ID
    """
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    raw_users=cur.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    userList=[s[0] for s in raw_users]
    return userList

def allMovieIds():
    """
    Returns a list with every movie ID
    """
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    raw_movies=cur.execute("SELECT movie_id FROM movies;").fetchall()
    conn.close()
    movieList=[s[0] for s in raw_movies]
    return movieList 

