import algo as main
from nltk import download
#import sql_requests_reco


"""
Il faudra peut-être découper en plusieurs fonctions parce que c'est débile de refaire sql_requests_reco.mostRatedByGenres() à chaque fois
et il faudra automatiser ça
sql_requests_reco.mostRatedByGenres() ça prend pas mal de temps, 5 sec environ
initSimMatrix c'est environ 12 secondes
SimMobies et percentiles prennent pas mal de temps aussi
"""

def init():
    download('stopwords')
    download('wordnet')
    main.initRatingsMatrix()
    main.realMoviesVector()
    main.realUsersVector()
    main.averageVector()
    main.initSimMatrix()
    main.initSimMoviesMatrix()
    main.initPercentilesMatrix()
    #sql_requests_reco.mostRatedByGenres()


init()
