import logging 

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def get_fav_movies(ratings_pivot, movieID, userID):
    """Find each user's favorite movie."""

    ratings_pivot_t = ratings_pivot.transpose()

    fav_movies = ratings_pivot_t.values.argmax(axis=1)
    fav_movies = [movieID[x] for x in fav_movies]
    fav_movies = pd.DataFrame(fav_movies, columns=["fav_movie"])

    fav_movies['userId'] = userID

    return fav_movies, ratings_pivot_t

def get_most_similar_movie(fav_movies, movieID, corr):
    """Find the most similar movie to each user's favorite movie."""

    fav_movies['most_similar_to_fav'] = fav_movies['fav_movie'].\
        apply(lambda x: movieID[np.argsort(-corr[movieID.index(x)])[1]])
    
    return fav_movies

def get_score(fav_movies, ratings_pivot_t):
    """Compute the satisfaction score as users average rating for the most similar movie."""
    
    fav_movies['most_similar_rating'] = fav_movies[['userId','most_similar_to_fav']].\
        apply(lambda x: ratings_pivot_t.loc[x[0],x[1]], axis=1)
    
    satisfaction = fav_movies.most_similar_rating
    satisfaction = satisfaction[satisfaction!=0].mean()

    return satisfaction

def evaluate(ratings_pivot, movieID, userID, corr):
    """Generate the final satisfaction score."""

    fav_movies, ratings_pivot_t = get_fav_movies(ratings_pivot, movieID, userID)
    fav_movies = get_most_similar_movie(fav_movies, movieID, corr)

    result = get_score(fav_movies, ratings_pivot_t)

    return result