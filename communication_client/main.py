import flask
import sql_requests
import bcrypt

app = flask.Flask(__name__)
app.config["DEBUG"] = True


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
    data = flask.request.form.to_dict()
    #hashes the password of the user with random salt
    data['password'] = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
    #ajouter un token généré automatiquement
    sql_requests.add_row('users', data)
    return ""

@app.route('/api/v0/resources/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    return sql_requests.delete_rows('users', 'user_id', user_id)

#idée = faire une requête qui s'exec à chaque fois qu'un utilisateur swipe. ce sera une requête PUT
#tant qu'il y a encore des gens qui n'ont pas swipé, ça se contente de dire que l'user qui vient de swiper a swipé 
# à GAUCHE OU à DROITE à la BDD
#genre y'a un champ has swiped dans la table users_groups
#et c'est 0 si a pas swipe, 1 s'il a swipe à droite, -1 s'il a swipe à gauche
#quand tout le monde a swipé, ça renvoie direct un nouveau film 
#du coup y'aurait genre une requete premier_film() et ensuite ce serait que des trucs en mode a_swipé()
#@app.route('/api/v0/', methods=[PUT])
#def 

#EN LOCAL:
#app.run()

#SUR LA VM:
app.run(host='0.0.0.0', port=80)

