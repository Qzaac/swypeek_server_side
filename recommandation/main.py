import numpy as np
import time

debut = time.time()
import sql_requests_reco as data

max_id_users = data.maxIdUsers()
max_id_movies = data.maxIdMovies()

#CE QUI PREND DU TEMPS C'EST initSimMatrix (environ 12 secondes) sur les 14 au total

#à chaque fois je mets des loads et des save (quand c'est des update)
#LE RISQUE : si j'exécute plusieurs fonctions par requete, commme je fais des loads à chaque fois je vais avoir 
# plusieurs fois la matrice dans la ram et donc c nul à chier
# du coup
# il faut que toutes les fonctions écrites ci-dessous se suffisent à elles-mêmes pour chaque requête 
#faudrait faire un init qui crée tous les fichiers .npy d'abord genre avec les fonctions 
#initratings, realmovies, realusers, averagevector (tous les trucs qui créent des fichiers .npy)

#android envoie une requête
#le serveur répond en loadant la liste qui a étée prélablament calculée
#elle pop le premier film, le renvoie à android
#elle save la nouvelle liste popée

#pour savoir 1. quand s'arrêter 2. comment modifier le classement en fct des swipes
#il faut stocker dans users_groups une colonne has_swiped avec true or false et faire des requêtes

def initRatingsMatrix():
    ratings = data.importRatings()

    matrix = np.full((max_id_users + 1, max_id_movies + 1), -1, dtype = float)
    
    for (user, movie, rating) in ratings
        matrix[user][movie] = rating

    np.save('ratings_matrix', matrix)
    return 0
    

def updateRatingsMatrix(user, movie):
    rating = data.importRating(user, movie)
    matrix = np.load('ratings_matrix.npy')
    matrix[user][movie] = rating
    np.save('ratings_matrix', matrix)
    return 0


#only used in proposition to check if a movie_id matches a real movie
def realMoviesVector():
    movie_ids = data.allMovieIds()
    vector = np.full(max_id_movies+1, 0)
    for movie in movie_ids:
        vector[movie] = 1
    np.save('real_movies', vector)
    return 0

#never used but same idea as realMoviesVector
def realUsersVector():
    user_ids = data.allUserIds()
    vector = np.full(max_id_users+1, 0)
    for user in user_ids:
        vector[user] = 1
    np.save('real_users', vector)
    return 0


def averageVector():
    vector = np.full(max_id_users + 1, 0, dtype = float)
    ratings_matrix = np.load('ratings_matrix.npy')

    for i in range(max_id_users + 1):
        boolean_vector = (ratings_matrix[i] != -1)
        sum = np.sum(boolean_vector*ratings_matrix[i])
        number_of_ratings = np.sum(boolean_vector)
        if(number_of_ratings == 0):
            vector[i] = 0
        else :
            vector[i] = sum/number_of_ratings
    
    np.save('average_vector', vector)

    return 0

def updateAverageVector(user):
    vector = np.load('average_vector.npy')
    ratings_matrix = np.load('ratings_matrix.npy')

    boolean_vector = (ratings_matrix[user] != -1)
    sum = np.sum(boolean_vector*ratings_matrix[user])
    number_of_ratings = np.sum(boolean_vector)
    if(number_of_ratings == 0):
        vector[user] = 0
    else :
        vector[user] = sum/number_of_ratings
    
    np.save('average_vector', vector)
    return 0


def sim(user1, user2, ratings_matrix, average_vector):
    boolean_vector = (ratings_matrix[user1] != -1)*(ratings_matrix[user2] != -1)
    movies_in_common = np.sum(boolean_vector)
    sum1 = np.sum(boolean_vector*(ratings_matrix[user1] - average_vector[user1])*(ratings_matrix[user2] - average_vector[user2]))
    sum2 = np.sum(boolean_vector*(ratings_matrix[user1] - average_vector[user1])**2)
    sum3 = np.sum(boolean_vector*(ratings_matrix[user2] - average_vector[user2])**2)


    if(movies_in_common==0 or sum2 == 0 or sum3 == 0):
        return 2
    
    return sum1/(np.sqrt(sum2*sum3))


def initSimMatrix():
    ratings_matrix = np.load('ratings_matrix.npy')
    average_vector = np.load('average_vector.npy')
    sim_matrix = np.zeros((max_id_users + 1, max_id_users + 1))
    
    for i in range(max_id_users + 1):
        sim_matrix[i][i] = 1
        for j in range(i+1, max_id_users + 1):
            sim_matrix[i][j] = sim(i,j, ratings_matrix, average_vector)
            sim_matrix[j][i] = sim_matrix[i][j]
        
    np.save('sim_matrix', sim_matrix)
    return 0


#so many parameters because don't want to load many times
def pred(user, movie, threshold, sim_matrix, ratings_matrix, average_vector):

    movie_ratings = ratings_matrix[:,movie]

    if_vector=(sim_matrix[user]!=2)*(movie_ratings != -1)*(sim_matrix[user] > threshold)
    sum1=np.sum(if_vector*sim_matrix[user]*(movie_ratings-average_vector))
    sum2=np.sum(if_vector*sim_matrix[user])
    
    if(sum2 == 0):
        return -1

    return average_vector[user] + sum1/sum2


def computePredMatrix(group_id, threshold):
    ratings_matrix = np.load('ratings_matrix.npy')
    average_vector = np.load('average_vector.npy')
    sim_matrix = np.load('sim_matrix.npy')

    user_list=data.user_list(group_id)
    pred_matrix = np.full((max_id_users+1, max_id_movies+1), -1, dtype=float)

    for user in user_list:
        for movie in range(max_id_movies + 1):
            if(ratings_matrix[user][movie] != -1):
                pred_matrix[user][movie] = ratings_matrix[user][movie]
            else:
                pred_matrix[user][movie] = pred(user, movie, threshold, sim_matrix, ratings_matrix, average_vector)

    return pred_matrix



def proposition(group_id, max_views, threshold = 0.8, limit=100):
    """
    given a group id and a maximum number of people who have seen a movie
    returns a sorted (by average of ratings and predictions) list of movie IDs with the average
        Parameters:
        - group_id: the ID of the group
        - max_views : if more people than max_views have rated a movie in the group, it won't be taken into account
        - threshold : defin
        - limit : the maximum number of movies in the list (100, for instance)
    if the final list is [] then no predictions could be made
    """
    user_list=data.user_list(group_id)
    real_movies = realMoviesVector()
    pred_matrix = computePredMatrix(group_id, threshold)
    movies_ranking=[]

    for movie in range(max_id_movies + 1):
        views=len(user_list)
        sum=0
        divide=len(user_list)

        for user in user_list:
            rating = ratings_matrix[user][movie]
            prediction = pred_matrix[user][movie]
            if(rating==-1):
                views-=1
                if(prediction==-1):
                    average = average_vector[user]
                    if(average!=0):
                        sum+=average
                    else:
                        divide-=1
                else:
                    sum+=prediction
            else:
                sum+=rating
        
        if(views <= max_views and real_movies[movie]==1 and divide!=0):
            average=sum/divide
            movies_ranking.append((movie, average))

    movies_ranking = sorted(movies_ranking, key=lambda t : t[1], reverse=True)[:limit]
    np.save('movies_ranking', movies_ranking)
    return 0

#alors en fait LOL il faut tout changer dès que : on ajoute/supprime film/user

#on a besoin de le recalculer dès qu'une nouvelle note apparaît (pas un swipe, genre une vraie note)
#ratings_matrix = initRatingsMatrix()
#créer update matrix
#print("après initRatingsMatrix:", time.time() - debut)
#il faut recalculer average_vecotr[i] quand une note change
#average_vector = averageVector()
#créer update vecotr
#print("après averageVector:", time.time() - debut)

#on pourrait modifier seulement les users qui ont vu le film dont la note vient d'être modifié MAIS plus simple de tout recalculer
#sim_matrix = initSimMatrix()
#print("après initSimMatrix:", time.time() - debut)
#calculer à chaque début de groupe
#pred_matrix = computePredMatrix(4, 0.8)
#print("après computePredMatrix:", time.time() - debut)
#update lorsque l'on ajoute un film ou lorsque l'on supprime un filmm
#faire un update
#print("après realMoviesVector:", time.time() - debut)

#calculer à chaque début de groupe
#print(proposition(4, 654654, 100))
#print("après proposition:", time.time() - debut)
