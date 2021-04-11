import flask
import flask_socketio as fsocket
import sql_requests
import numpy as np
import bcrypt
import sys
sys.path.insert(1, '../recommandation')
import algo

app = flask.Flask(__name__)
app.config["DEBUG"] = True
socketio = fsocket.SocketIO(app)

root = "/home/qzaac/tetech1A/PACT/seveur"
path_to_data = "/recommandation/data/"


def dict_factory(cursor, row):
    """used to turn lists into dictionaries while using sqlite
    because it's more convenient using json"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# this is what appears when one goes to the home page of the url
@app.route('/', methods=['GET'])
def home():
    return "<h1>API Swypeek</h1><p>This site is a prototype API for a college project.</p>"

@app.route('/api/v0/resources/users', methods=['GET'])
def existing_user():
    return sql_requests.existing_user()

@app.route('/api/v0/resources/users/connection', methods=['PUT'])
def check_credentials():
    return sql_requests.check_credentials()

@app.route('/api/v0/resources/users', methods=['POST'])
def add_row_users():
    """
    add a user and returns its id
    """
    data = flask.request.form.to_dict()
    #hashes the password of the user with random salt
    data['password'] = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
    #TODO: ajouter un token généré automatiquement
    return str(sql_requests.add_row('users', data))


@app.route('/api/v0/resources/groups', methods=['POST'])
def add_row_groups():
    """
    add a group and returns its id
    """
    data = flask.request.form.to_dict()
    return str(sql_requests.add_row('groups', data))


@app.route('/api/v0/resources/users_groups', methods=['POST'])
def add_row_users_groups():
    data = flask.request.form.to_dict()
    str(sql_requests.add_row('users_groups', data))
    return ""

@app.route('/api/v0/resources/groups/connection', methods=['PUT'])
def check_group_credentials():
    """returns group_id on success"""
    return sql_requests.check_group_credentials()

@app.route('/api/v0/resources/movie')
def getMovieSpec():
    """returns a dictionnary with all specs of a movie given in the database"""
    movie_id = flask.request.args.get('movie_id')
    return sql_requests.getMovieSpec(movie_id)



@app.route('/api/v0/resources/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    return sql_requests.delete_rows('users', 'user_id', user_id)


@app.route('/api/v0/start_small_group', methods=['GET'])
def startSmallGroup():
    group_id = flask.request.args.get('group_id')
    algo.proposition(int(group_id))
    movies_ranking = np.load(root + path_to_data + 'movies_ranking_group' + group_id + '.npy')
    if(movies_ranking.size == 0):
        #if there's no movie to return, return a special negative value
        return '-3'
    else:    
        movie_id = movies_ranking[0][0]
        np.save(root + path_to_data + 'movies_ranking_group' + group_id, movies_ranking[1:])
        return str(int(movie_id))


@app.route('/api/v0/get_new_movie', methods=['PUT'])
def getNewMovie():
    data = flask.request.form
    #data must contain the direction of the swipe swipe_direction (1 or -1), the group_id and the user_id
    swipe_list = sql_requests.update_has_swiped(data.get('group_id'), data.get('user_id'), data.get('swipe_direction'))
    
    everyone_swiped = True
    everyone_swiped_right = True

    #algo.refreshClassement(movie_id, swipe_list)

    for swipe in swipe_list:
        if(swipe == 0):
            everyone_swiped = False
            everyone_swiped_right = False
        if(swipe == -1):
            everyone_swiped_right = False

    if(everyone_swiped):
        if(everyone_swiped_right):
            #essentially means a movie was found so the group can be deleted
            sql_requests.delete_rows('groups', 'group_id', data.get('group_id'))
            return '-2'
        else:
            #we need to find another movie and to reset has swiped!
            sql_requests.reset_has_swiped(data.get('group_id'))
            movies_ranking = np.load(root + path_to_data + 'movies_ranking_group' + data.get('group_id') + '.npy')
            if(movies_ranking.size == 0):
                #if there's no movie to return, return a special negative value
                return '-3'
            else:    
                movie_id = movies_ranking[0][0]
                np.save(root + path_to_data + 'movies_ranking_group' + data.get('group_id'), movies_ranking[1:])
                return str(int(movie_id))
    else:
        #some people still haven't swiped
        return '-1'



#quand un utilisateur envoie un socket 'join' avec le group_id dans le message ça le rajoute à la room qui port le numéro du group_id
@socketio.on('join')
def on_join(group_id):
    fsocket.join_room(group_id)


#quand un utilisateur démarre le début des prédictions on envoie le film à tous les autres
#ou bien lorsqu'un utilisateur swipe et est le dernier a swipé et un film est proposé
@socketio.on('new_movie')
def on_start(data):
    group_id = data.get('group_id')
    movie_id = data.get('movie_id')
    fsocket.emit('movie_id', movie_id, room=group_id)



#EN LOCAL:
socketio.run(app)

#SUR LA VM:
#socketio.run(app, host='0.0.0.0', port=80)

