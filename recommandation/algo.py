import numpy as np
import time
from nltk import *
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import sql_requests_reco as data

max_id_users = data.maxIdUsers()
max_id_movies = data.maxIdMovies()
genre_ids = [3, 1, 4, 7, 2, 8, 6, 11, 13, 18] #ids of the 9 more popular genres + (the last one is animation)

#PATH d'auré
#root = "/home/qzaac/tetech1A/PACT/code serveur"
#path_to_data = "/recommandation/data/"
#PATH de zako
#root = "/users/Zac/Documents/serveur"
#path_to_data = "/recommandation/data/"
#PATH du serveur
root = "/home/ubuntu/serveur"
path_to_data = "/recommandation/data/"


#only used in proposition to check if a movie_id matches a real movie
def realMoviesVector():
    max_id_movies = data.maxIdMovies()
    movie_ids = data.allMovieIds()
    vector = np.full(max_id_movies+1, 0)
    for movie in movie_ids:
        vector[movie] = 1
    np.save(root + path_to_data + 'real_movies', vector)
    return 0


#never used but same idea as realMoviesVector
def realUsersVector():
    max_id_users = data.maxIdUsers()
    user_ids = data.allUserIds()
    vector = np.full(max_id_users+1, 0)
    for user in user_ids:
        vector[user] = 1
    np.save(root + path_to_data + 'real_users', vector)
    return 0


def initRatingsMatrix():
    max_id_movies = data.maxIdMovies()
    max_id_users = data.maxIdUsers()
    ratings = data.importRatings()

    matrix = np.full((max_id_users + 1, max_id_movies + 1), -1, dtype = float)
    
    for (user, movie, rating) in ratings:
        matrix[user][movie] = rating

    np.save(root + path_to_data + 'ratings_matrix', matrix)
    return 0


def scrub_words(text): 
    # remove html markup
    text=re.sub("(<.*?>)","",text)
    #remove non-ascii and digits
    text=re.sub("(\\W|\\d)"," ",text)
    #remove whitespace
    text=text.strip()
    return text


def shortlist(words):
    """deletes useless words"""
    stopWords = set(corpus.stopwords.words('english'))
    shortlisted_words=[]
    for w in words:
        if w not in stopWords:
            shortlisted_words.append(w)
        if w == '':
            shortlisted_words.remove(w)
    return shortlisted_words    


def initSimMoviesMatrix():
    max_id_movies = data.maxIdMovies()
    """saves in data a matrix of shape (max_id_movies + 1, max_id_movies + 1) of
    similarity between synopses such that matrix[i][j]=np.nan if i or j don't correspond to a real movie"""

    """also saves the list of percentiles"""
    synopses_filled = ["rine"]*(max_id_movies+1)
    updatedsynopsis=[]
    synopses=data.allSynopses()
    
    for (movie_id, synopsis) in synopses :
        synopses_filled[movie_id]=synopsis

    lemmatizer = WordNetLemmatizer()
    
    #simplify each synopsis and append it to a list (of list)
    for s in synopses_filled :
        words = word_tokenize(s)
        #lowercase for everyone
        lower_words=[word.lower() for word in words]
        #Noise cancelling
        cleaned_words=[scrub_words(w) for w in lower_words]
        #Lemmatization
        lemmatized_words=[lemmatizer.lemmatize(word=word,pos='v') for word in cleaned_words]
        #get rid of useless words
        shortlisted_words=shortlist(lemmatized_words)
        updatedsynopsis.append(shortlisted_words)

    #list of simplified synopses
    corpus = []
    for s in updatedsynopsis :
        corpus.append(' '.join(s))

    vect = TfidfVectorizer(min_df=1, stop_words="english")
    tfidf = vect.fit_transform(corpus)
    pairwise_similarity = (tfidf * tfidf.T).toarray()
    
    for i in range(max_id_movies+1):
        for j in range(i+1, max_id_movies+1):
            #if the i and j are much to similare they aren't real movies (false movies' synopses have been filled with the same string)
            if pairwise_similarity[i][j] >= 1:
                pairwise_similarity[i][j]=np.nan
                pairwise_similarity[j][i]=np.nan
    
    stats = pairwise_similarity.reshape(-1)
    percentiles=[]
    for i in range(101):
        percentiles.append(np.nanpercentile(stats, i))

    np.save(root + path_to_data + 'percentiles', np.array(percentiles))
    np.save(root + path_to_data + 'movies_sim_matrix', pairwise_similarity)
    return 0


def initPercentilesMatrix():
    """saves a np array of shape (max_id_movies+1, max_id_movies+1) such that
    percentiles_matrix[i][j] returns in which percentile the similarity between i and j is (among all real movies)"""
    max_id_movies = data.maxIdMovies()
    movies_sim_matrix = np.load(root + path_to_data + 'movies_sim_matrix.npy')
    matrix = np.full((max_id_movies+1, max_id_movies+1), np.nan, dtype=float)
    percentiles = np.load(root + path_to_data + 'percentiles.npy')

    for i in range(max_id_movies+1):
        for j in range(i, max_id_movies+1):
            sim = movies_sim_matrix[i][j]
            if not(np.isnan(sim)):
                for index, p in enumerate(percentiles):
                    if sim<p:
                        matrix[i][j]=(index-1)/100
                        matrix[j][i]=(index-1)/100
                        break;

    np.save(root + path_to_data + 'percentiles_matrix', matrix)
    return 


def updateRatingsMatrix(user, movie):
    rating = data.importRating(user, movie)
    matrix = np.load(root + path_to_data + 'ratings_matrix.npy')
    
    matrix[user][movie] = rating
    np.save(root + path_to_data + 'ratings_matrix', matrix)
    return 0


def averageVector():
    max_id_users = data.maxIdUsers()
    vector = np.full(max_id_users + 1, 0, dtype = float)
    ratings_matrix = np.load(root + path_to_data + 'ratings_matrix.npy')

    for i in range(max_id_users + 1):
        boolean_vector = (ratings_matrix[i] != -1)
        sum = np.sum(boolean_vector*ratings_matrix[i])
        number_of_ratings = np.sum(boolean_vector)
        if(number_of_ratings == 0):
            vector[i] = 0
        else :
            vector[i] = sum/number_of_ratings
    
    np.save(root + path_to_data + 'average_vector', vector)

    return 0


def updateAverageVector(user):
    vector = np.load(root + path_to_data + 'average_vector.npy')
    ratings_matrix = np.load(root + path_to_data + 'ratings_matrix.npy')

    boolean_vector = (ratings_matrix[user] != -1)
    sum = np.sum(boolean_vector*ratings_matrix[user])
    number_of_ratings = np.sum(boolean_vector)
    if(number_of_ratings == 0):
        vector[user] = 0
    else :
        vector[user] = sum/number_of_ratings
    np.save(root + path_to_data + 'average_vector', vector)
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
    max_id_users = data.maxIdUsers()
    ratings_matrix = np.load(root + path_to_data + 'ratings_matrix.npy')
    average_vector = np.load(root + path_to_data + 'average_vector.npy')
    sim_matrix = np.zeros((max_id_users + 1, max_id_users + 1))
    
    for i in range(max_id_users + 1):
        sim_matrix[i][i] = 1
        for j in range(i+1, max_id_users + 1):
            sim_matrix[i][j] = sim(i,j, ratings_matrix, average_vector)
            sim_matrix[j][i] = sim_matrix[i][j]
        
    np.save(root + path_to_data + 'sim_matrix', sim_matrix)
    return 0


def updateSimMatrix(user):
    max_id_users = data.maxIdUsers()
    ratings_matrix = np.load(root + path_to_data + 'ratings_matrix.npy')
    average_vector = np.load(root + path_to_data + 'average_vector.npy')
    sim_matrix = np.load(root + path_to_data + 'sim_matrix.npy')

    length=sim_matrix.shape[0]
    add=user-length
    if(add>=0):
        sim_matrix.resize((length+add+1,length+add+1))

    for i in range(max_id_users+1):
        sim_matrix[i][user] = sim(i,user, ratings_matrix, average_vector)
        sim_matrix[user][i] = sim_matrix[i][user]
    
    np.save(root + path_to_data + 'sim_matrix', sim_matrix)
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


def computePredMatrix(group_id, threshold, ratings_matrix, average_vector):
    max_id_movies = data.maxIdMovies()
    max_id_users = data.maxIdUsers()
    sim_matrix = np.load(root + path_to_data + 'sim_matrix.npy')
    user_list=data.user_list(group_id)
    pred_matrix = np.full((max_id_users+1, max_id_movies+1), -1, dtype=float)

    for user in user_list:
        for movie in range(max_id_movies + 1):
            if(ratings_matrix[user][movie] != -1):
                pred_matrix[user][movie] = ratings_matrix[user][movie]
            else:
                pred_matrix[user][movie] = pred(user, movie, threshold, sim_matrix, ratings_matrix, average_vector)

    return pred_matrix


def proposition(group_id, threshold = 0.8, limit=100):
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
    max_id_movies = data.maxIdMovies()
    user_list=data.user_list(group_id)
    max_views=len(user_list)
    real_movies = np.load(root + path_to_data + 'real_movies.npy')
    ratings_matrix = np.load(root + path_to_data + 'ratings_matrix.npy')
    average_vector = np.load(root + path_to_data + 'average_vector.npy')
    pred_matrix = computePredMatrix(group_id, threshold, ratings_matrix, average_vector)
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
        
        if(views < max_views and real_movies[movie]==1 and divide!=0):
            average=sum/divide
            movies_ranking.append((movie, average))

    movies_ranking = sorted(movies_ranking, key=lambda t : t[1], reverse=True)[:limit]

    np.save(root + path_to_data + 'movies_ranking_group' + str(group_id), movies_ranking)
    return 0


def firstMovies():
    """based on the list of lists, returns 20 movie_id chosen randomly
    (we choose 2 movies randomly for each genre in genre_ids in the most rated movies of this genre)"""
    most_rated_by_genres = np.load(root + path_to_data + 'most_rated_by_genres.npy')
    first_movies = []
    for genre_id in genre_ids:
        top_movies_by_genre = most_rated_by_genres[genre_id]
        for k in range(2):
            i = np.random.randint(0,25)
            while(top_movies_by_genre[i] in first_movies):
                i = (i+1)%25
            first_movies.append(top_movies_by_genre[i])

    return first_movies


def refreshRanking(swiped_movie_id, swipe_list, group_id):
    movies_ranking = np.load(root + path_to_data + 'movies_ranking_group' + str(group_id) + '.npy')
    percentiles_matrix = np.load(root + path_to_data + 'percentiles_matrix.npy')
    s = np.array(swipe_list).sum()
    nbr_of_users = len(swipe_list)

    for i, (movie_id, ranking) in enumerate(movies_ranking):
        genres_in_common = data.numberCommonGenres(swiped_movie_id, int(movie_id))
        min_number_genres = data.minNumberGenres(swiped_movie_id, int(movie_id))
        percentile = percentiles_matrix[int(swiped_movie_id)][int(movie_id)]
        movies_ranking[i][1] = ranking*(1 + s/nbr_of_users*(percentile**2 + (1 - percentile)*genres_in_common/min_number_genres))/2

    movies_ranking = sorted(movies_ranking, key=lambda t : t[1], reverse=True)

    np.save(root + path_to_data + 'movies_ranking_group' + str(group_id), movies_ranking)
    return 0
