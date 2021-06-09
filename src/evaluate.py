"""Model evaluation."""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def get_fav_movies(ratings_pivot, movie_id, user_id):
    """
    For each user, find his or her favorite movie, which is his or her best-rated movie.

    Args:
        ratings_pivot (pandas.DataFrame) - the pivoted ratings dataframe
        movie_id (numpy.array) - the movie IDs used in model training
        user_id (numpy.array) - the user IDs used in model training

    Returns:
        fav_movies (pandas.DataFrame) - the dataframe aggregated by user, consisting of
        each user's favorite movie ID
        ratings_pivot_t (pandas.DataFrame) - the transpose of ratings pivot dataframe
    """
    if not isinstance(ratings_pivot, pd.DataFrame):
        logger.error("Provided argument `ratings_pivot` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `ratings_pivot` is not a Panda's DataFrame object")

    ratings_pivot_t = ratings_pivot.transpose()
    ratings_pivot_t.index = user_id
    ratings_pivot_t.columns = movie_id # add indices

    fav_movies = ratings_pivot_t.values.argmax(axis=1)
    fav_movies = [movie_id[x] for x in fav_movies]
    fav_movies = pd.DataFrame(fav_movies, columns=["fav_movie"])

    fav_movies['userId'] = user_id

    return fav_movies, ratings_pivot_t

def get_most_similar_movie(fav_movies, movie_id, corr):
    """
    For each user, find the most-similar movie to his or her favorite movie.

    Args:
        fav_movies (pandas.DataFrame) - the dataframe aggregated by user, consisting of
        each user's favorite movie ID
        movie_id (numpy.array) - the movie IDs used in model training
        corr (numpy.array) - the correlation matrix from model training

    Returns:
        fav_movies (pandas.DataFrame) - the updated favorate movies dataframe,
        consisting of each user's favorite movie ID, and the most-similar movie to that
        favorite movie.
    """
    if not isinstance(fav_movies, pd.DataFrame):
        logger.error("Provided argument `fav_movies` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `fav_movies` is not a Panda's DataFrame object")

    # recommend movie based on the favorite movie
    fav_movies['most_similar_to_fav'] = fav_movies['fav_movie'].\
        apply(lambda x: movie_id[np.argsort(-corr[movie_id.index(x)])[1]])

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
    # 0 rating means the user has not watched the movie
    satisfaction = satisfaction[satisfaction!=0].mean()

    logger.info("The average satisfaction score is %.2f", satisfaction)

    return satisfaction

def evaluate(ratings_pivot, movie_id, user_id, corr):
    """Generate the final satisfaction score."""
    # load index lists
    movie_id = movie_id.tolist()
    user_id = user_id.tolist()

    fav_movies, ratings_pivot_t = get_fav_movies(ratings_pivot, movie_id, user_id)
    fav_movies = get_most_similar_movie(fav_movies, movie_id, corr)
    result = get_score(fav_movies, ratings_pivot_t)

    return result
