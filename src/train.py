import logging 

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def get_rating_matrix(ratings):
    """Generate the rating matrix, row by movieId and column by userId."""

    ratings_pivot = ratings.pivot(index='movieId',columns='userId', values='rating').fillna(0)

    movieID = ratings_pivot.index
    userID = ratings_pivot.columns

    logger.info("The rating matrix of shape (%d,%d) is generated.", ratings_pivot.shape[0], ratings_pivot.shape[1])

    return ratings_pivot, movieID, userID

def compute_distance(ratings_pivot):
    """The model training step, where a distance matrix for movies is computed."""

    corr = np.corrcoef(ratings_pivot)

    logger.info("The movie distance/correlation matrix of shape (%d,%d) is generated.", corr.shape[0], corr.shape[1])

    return corr

def train(ratings):
    """Perform all model training steps."""

    ratings_pivot, movieID, userID = get_rating_matrix(ratings)
    corr = compute_distance(ratings)

    return ratings_pivot, movieID, userID, corr