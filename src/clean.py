import logging 

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def merge_data(movies, links):
    """
    Match movie titles with external ids like imdbId and doubanId.

    Args:
        movies (pandas.DataFrame) - movies dataframe
        links (pandas.DataFrame) - links dataframe

    Returns:
        movies_merged (pandas.DataFrame) - the merged movies dataframe
    """

    if not isinstance(movies, pd.DataFrame):
        logger.error("Provided argument `movies` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `movies` is not a Panda's DataFrame object")

    if not isinstance(links, pd.DataFrame):
        logger.error("Provided argument `links` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `links` is not a Panda's DataFrame object")

    movies_merged = links.merge(movies, left_on="movieId", right_on="movieId")

    return movies_merged

def filter(ratings, user_min=50, movie_min=50):
    """
    Drop users and movies with few ratings.

    Args:
        ratings (pandas.DataFrame) - ratings dataframe
        user_min (int) - the minimum number of ratings a user needs to have
        movie_min (int) - the minimum number of ratings a movie needs to have

    Returns:
        ratings (pandas.DataFrame) - the filtered ratings dataframe
    """

    if not isinstance(ratings, pd.DataFrame):
        logger.error("Provided argument `ratings` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `ratings` is not a Panda's DataFrame object")

    # filter out users with less than user_min ratings
    user_rating_count = ratings['userId'].value_counts()
    ratings = ratings[ratings['userId'].isin(user_rating_count[user_rating_count>=user_min].index)]

    logger.info('Ratings of users with less than %d ratings are dropped', user_min)

    # filter out movies with less than movie_min ratings
    movie_rating_count = ratings['movieId'].value_counts()
    ratings = ratings[ratings['movieId'].isin(movie_rating_count[movie_rating_count>=movie_min].index)]

    logger.info('Ratings of movies with less than %d ratings are dropped', movie_min)

    return ratings

def clean(movies, links, ratings, config):
    """Perform all data cleaning and returns the cleaned dataframes."""

    movies = merge_data(movies, links)
    ratings = filter(ratings, **config['filter'])

    return movies, ratings