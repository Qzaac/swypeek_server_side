import algo as main
from nltk import download
import sql_requests_reco


def init():
    download('stopwords')
    download('wordnet')
    download('punkt')
    main.initRatingsMatrix()
    main.realMoviesVector()
    main.realUsersVector()
    main.averageVector()
    main.initSimMatrix()
    main.initSimMoviesMatrix()
    main.initPercentilesMatrix()
    sql_requests_reco.mostRatedByGenres()


init()
