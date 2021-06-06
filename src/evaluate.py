import logging 

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def get_fav_movies(ratings_pivot, movieID, userID):
    """
    For each user, find his or her favorite movie by identifying his or her best-rated
    movie.

    Args:
        ratings_pivot (pandas.DataFrame) - the pivoted ratings dataframe
        movieID (numpy.array) - the movie IDs used in model training
        userID (numpy.array) - the user IDs used in model training

    Returns:
        fav_movies (pandas.DataFrame) - the dataframe aggregated by user, consisting of 
        each user's favorite movie ID
        ratings_pivot_t (pandas.DataFrame) - the transpose of ratings pivot dataframe
    """
    
    if not isinstance(ratings_pivot, pd.DataFrame):
        logger.error("Provided argument `ratings_pivot` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `ratings_pivot` is not a Panda's DataFrame object")

    ratings_pivot_t = ratings_pivot.transpose()
    ratings_pivot_t.index = userID; ratings_pivot_t.columns = movieID # add indices

    fav_movies = ratings_pivot_t.values.argmax(axis=1)
    fav_movies = [movieID[x] for x in fav_movies]
    fav_movies = pd.DataFrame(fav_movies, columns=["fav_movie"])

    fav_movies['userId'] = userID

    return fav_movies, ratings_pivot_t

def get_most_similar_movie(fav_movies, movieID, corr):
    """
    For each user, find the most-similar movie to his or her favorite movie.

    Args:
        fav_movies (pandas.DataFrame) - the dataframe aggregated by user, consisting of 
        each user's favorite movie ID
        movieID (numpy.array) - the movie IDs used in model training
        corr (numpy.array) - the correlation matrix from model training

    Returns:
        fav_movies (pandas.DataFrame) - the updated favorate movies dataframe, 
        consisting of each user's favorite movie ID, and the most-similar movie to that
        favorite movie.
    """

    if not isinstance(fav_movies, pd.DataFrame):
        logger.error("Provided argument `fav_movies` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `fav_movies` is not a Panda's DataFrame object")

    fav_movies['most_similar_to_fav'] = fav_movies['fav_movie'].\
        apply(lambda x: movieID[np.argsort(-corr[movieID.index(x)])[1]])
    
    return fav_movies

def get_score(fav_movies, ratings_pivot_t):
    """
    Compute the satisfaction score as users average rating for the most similar movie.

    Args:
        fav_movies (pandas.DataFrame) - the favorate movies dataframe, consisting of each 
        user's favorite movie ID, and the most-similar movie to that favorite movie.
        ratings_pivot_t (pandas.DataFrame) - the transpose of ratings pivot dataframe

    Returns:
        satisfaction (float) - the average satisfaction score that defines the success 
        of the app
    """
    
    if not isinstance(fav_movies, pd.DataFrame):
        logger.error("Provided argument `fav_movies` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `fav_movies` is not a Panda's DataFrame object")

    if not isinstance(ratings_pivot_t, pd.DataFrame):
        logger.error("Provided argument `ratings_pivot_t` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `ratings_pivot_t` is not a Panda's DataFrame object")

    fav_movies['most_similar_rating'] = fav_movies[['userId','most_similar_to_fav']].\
        apply(lambda x: ratings_pivot_t.loc[x[0],x[1]], axis=1)
    
    satisfaction = fav_movies.most_similar_rating
    satisfaction = satisfaction[satisfaction!=0].mean()

    return satisfaction

def evaluate(ratings_pivot, movieID, userID, corr):
    """Generate the final satisfaction score."""

    movieID = movieID.tolist(); userID = userID.tolist()

    fav_movies, ratings_pivot_t = get_fav_movies(ratings_pivot, movieID, userID)
    fav_movies = get_most_similar_movie(fav_movies, movieID, corr)
    result = get_score(fav_movies, ratings_pivot_t)

    return result