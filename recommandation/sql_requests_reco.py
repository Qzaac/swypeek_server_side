import sqlite3
import numpy as np

#PATH when on the VM
#data_file='/home/ubuntu/serveur/swypeek_updated.db'

#Normal PATH
data_file='../swypeek_updated.db'

#PATH doréli1
#root = "/home/qzaac/tetech1A/PACT/seveur"
#PATH de zako
root = "/users/Zac/Documents/serveur"
path_to_data = "/recommandation/data/"
#PATH du serveur
#root = "/home/ubuntu/serveur"
#path_to_data = "/recommandation/data/"

genre_ids = [3, 1, 4, 7, 2, 8, 6, 11, 13, 18] #ids of the 9 more popular genres + (the last one is animation)


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

def mostRatedByGenres():
    """Returns a list of list containing movie_id of the 25 most rated movies by genres:
    there are 21 genres in total
    even if we chose 10 genres (see global variable genre_ids) we decided that most_rated_by_genres[i] should return the top25 for the
    genre i, and that it should be full of zeros if the genre is not in genre_ids"""
    conn = sqlite3.connect(data_file)
    cur = conn.cursor()
    most_rated_by_genres=np.zeros((22,25))
    for genre_id in genre_ids:
        most_rated_by_genres[genre_id] = [i[0] for i in cur.execute("""
            SELECT movies.movie_id
            FROM genres 
                INNER JOIN genres_movies 
                    ON genres.genre_id = genres_movies.genre_id 
                INNER JOIN movies 
                    ON movies.imdb_id = genres_movies.imdb_id
                WHERE genres.genre_id = ?
                ORDER BY movies.votes_number DESC
                LIMIT 25;""", [genre_id]).fetchall()]
    np.save(root + path_to_data + 'most_rated_by_genres', most_rated_by_genres)
    conn.close()
    
