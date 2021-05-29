import logging 

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def merge_data(movies, links):
    """Match movie titles with external ids like imdbId and doubanId."""

    movies_merged = links.merge(movies, left_on="movieId", right_on="movieId")

    return movies_merged

def filter(ratings, user_min=50, movie_min=50):
    """Drop users and movies with few ratings."""

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