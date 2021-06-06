import logging 

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def get_rating_matrix(ratings):
    """
    Generate the rating matrix, row by movieId and column by userId.

    Args:
        ratings (pandas.DataFrame) - cleaned ratings dataframe

    Returns:
        ratings_pivot (pandas.DataFrame) - the pivoted ratings dataframe
        movieID (list) - the movie IDs used for modeling
        userID (list) - the user IDs used for modeling
    """

    if not isinstance(ratings, pd.DataFrame):
        logger.error("Provided argument `ratings` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `ratings` is not a Panda's DataFrame object")

    ratings_pivot = ratings.pivot(index='movieId',columns='userId', values='rating').fillna(0)

    movieID = ratings_pivot.index
    userID = ratings_pivot.columns

    logger.info("The rating matrix of shape (%d,%d) is generated.", ratings_pivot.shape[0], 
    ratings_pivot.shape[1])

    return ratings_pivot, movieID, userID

def compute_distance(ratings_pivot):
    """
    The model training step, where a distance matrix / correlation score for each
    pair of movies is computed.

    Args:
        ratings_pivot (pandas.DataFrame) - the pivoted ratings dataframe

    Returns:
        corr (numpy.array) - the correlation / distance matrix (the trained model object for 
        collaborative filtering algorithm)
    """

    if not isinstance(ratings_pivot, pd.DataFrame):
        logger.error("Provided argument `ratings_pivot` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `ratings_pivot` is not a Panda's DataFrame object")

    corr = np.corrcoef(ratings_pivot)

    logger.info("The movie distance/correlation matrix of shape (%d,%d) is generated.", corr.shape[0], 
    corr.shape[1])

    return corr

def train(ratings):
    """
    Perform all model training steps.

    Args:
        ratings (pandas.DataFrame) - the cleaned ratings dataframe

    Returns:
        ratings_pivot (pandas.DataFrame) - the pivoted ratings dataframe
        movieID (list) - the movie IDs used for modeling
        userID (list) - the user IDs used for modeling
        corr (numpy.array) - the correlation / distance matrix (the trained model object for 
        collaborative filtering algorithm)
    """

    ratings_pivot, movieID, userID = get_rating_matrix(ratings)
    corr = compute_distance(ratings_pivot)

    return ratings_pivot, movieID, userID, corr