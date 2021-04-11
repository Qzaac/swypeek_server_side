import requests
import json

#EN LOCAL:
url = 'http://127.0.0.1:5000'

#SUR LA VM:
#url = 'http://pact11.r2.enst.fr:80'

# ---------CREATE AN ACCOUNT--------- #

# creates a new user with nickname, age, email and password :
# this is a POST request, it needs to come with a form
# /!\ keys of the dictionary (the form) should be the name of the columns of the db


def add_account(data):
    """ creates a new user
    this is a POST request it needs to come with a form
    /!\ keys of the dictionary (the form) should be the name of the columns of the db """
    # example of data : {'username':'Aurélien', 'created_at':'2020', 'birth_date':'2000',
    #  'email':'acastre@enst.fr', 'password':'admin', 'main_language':1, 'token_value':'35435431384', 'expiration_date':'2022'}
    x = requests.post(url + '/api/v0/resources/users', data=data)
    print(x.text)

def add_group(data):
    """ creates a new group
    this is a POST request it needs to come with a form
    /!\ keys of the dictionary (the form) should be the name of the columns of the db """
    # example of data : {'group_name':'pact11', 'created_at':'2020-04-15', 'group_code':'secured', 'group_max_size':900, 'group_current_size':1}
    x = requests.post(url + '/api/v0/resources/groups', data=data)
    print(x.text)

def add_user_to_group(data):
    """ adds a user to a group
    this is a POST request it needs to come with a form
    /!\ keys of the dictionary (the form) should be the name of the columns of the db """
    # example of data : {'user_id':'42', 'group_id':'5', 'nickname':'jeanjass'}
    x = requests.post(url + '/api/v0/resources/users_groups', data=data)
    print(x.text)

def existing_user(email):
    """returns the account ID if the email is found, otherwise returns []"""
    # example of email: 'acastre@enst.fr'
    x = requests.get(url + '/api/v0/resources/users?email=' + email)
    print(json.dumps(x.json(), sort_keys=True, indent=4))

def get_movie_spec(movie_id):
    x = requests.get(url + '/api/v0/resources/movie?movie_id='+str(movie_id))
    print(x.text)


# ---------CONNECTION--------- #

def check_credentials(data):
    """if username/email/password combination is correct, modify the token and the expiration date and returns it"""
    #example of data: {'email-username':'acastre@enst.fr', 'password':'admin'}
    x=requests.put(url + '/api/v0/resources/users/connection', data=data)
    print(x.text)


def check_group_credentials(data):
    #example of data: {'group_name':'pact11', 'group_code':'secured'}
    x=requests.put(url + '/api/v0/resources/groups/connection', data=data)
    print(x.text)


# ---------OTHER USEFUL REQUESTS--------- #

def delete_user(userid):
    x = requests.delete(url + '/api/v0/resources/users/' + userid)
    print(x.text)


def startSmallGroup(group_id):
    x = requests.get(url + '/api/v0/start_small_group?group_id=' + str(group_id))
    print(x.text)


def getNewMovie(data):
    #example of data: {'group_id':'4', 'user_id':'92', 'swipe_direction':'-1'}
    x = requests.put(url+'/api/v0/get_new_movie', data=data)
    print(x.text)


"""
query = input()

if(query=="add_account"):
    add_account({'username':'Aurelien', 'created_at':'2020-05-20', 'birth_date':'2000-01-20', 'email':'acastre@enst.fr', 'password':'admin', 'main_language':1, 'token_value':'35435431384', 'expiration_date':'2022-05-02'})
elif(query=="existing_user"):
    email=input()
    existing_user(email)
elif(query=="check_credentials"):
    check_credentials({'email':'acastre@enst.r', 'password':'admin'}) #wrong email
    check_credentials({'email':'acastre@enst.fr', 'password':'admn'}) #wrong pwd
    check_credentials({'email':'acastre@enst.fr', 'password':'admin'}) #everything is right !
elif(query=="delete_user"):
    user=input()
    delete_user(user)
else:
    print("Please type one of these : add_account, existing_user, check_credentials, delete_user")
"""

#startSmallGroup(4)
#add_group({'group_name':'pact11', 'created_at':'2020-04-15', 'group_code':'secured', 'group_max_size':900})
#add_user_to_group({'user_id':'42', 'group_id':'5', 'nickname':'jeanjass'})
#check_group_credentials({'group_name':'pact11', 'group_code':'secured'})
#getNewMovie({'group_id':'4', 'user_id':'97', 'swipe_direction':'-1'})
get_movie_spec(6)