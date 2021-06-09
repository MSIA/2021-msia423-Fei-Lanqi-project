"""Prediction script."""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def predict_aux(dist_list, movie_id):
    """
    Auxilliary function that ranks other movies based on similarity for a given movie.

    Args:
        dist_list (np.array) - the distance array for a movie
        movie_id (np.array) - the list of movie IDs used in model training
    Returns:
        result (np.array) - the movie ID list, ranked by similarity to the input movie, excluding
        the input movie.
    """
    if len(dist_list) > len(movie_id):
        logger.error("Provided `movie_id` has smaller length than `dist_list`")
        raise IndexError("Provided `movie_id` has smaller length than `dist_list`")

    result = np.argsort(-dist_list)
    result = [movie_id[i] for i in result]
    result = np.array(result[1:]) # discard the most similar movie, which is itself

    return result

def predict_matrix(corr, movie_id):
    """
    Get the predictions (the similar movies) in a matrix form.

    Args:
        corr (numpy.array) - the trained model object, correlation matrix from model training step
        movie_id (numpy.array) - the list of movie IDs used in model training
    Returns:
        prediction matrix (numpy.array) - the predictions, each row is the result list 
        (described in previous function) for a particular movie
    """
    if not isinstance(corr, np.ndarray):
        logger.error("Provided argument `corr` is not a Numpy.Array object")
        raise TypeError("Provided argument `corr` is not a Numpy.Array object")

    # the predictions in matrix format
    prediction_matrix = np.array([predict_aux(x, movie_id) for x in corr])

    return prediction_matrix

def predict_df(prediction_matrix, movie_id, top_n = 10):
    """
    Transform the prediction matrix into a pandas dataframe with appropriate indices.

    Args:
        prediction_matrix (numpy.array) - the prediction matrix from last step
        movie_id (numpy.array) - the list of movie IDs used in model training
        top_n (int) - how many recommendations to be generated for each movie
    Returns:
        prediction_df (pandas.DataFrame) - the predictions matrix in pandas dataframe format
    """
    if not isinstance(prediction_matrix, np.ndarray):
        logger.error("Provided argument `prediction_matrix` is not a Numpy.Array object")
        raise TypeError("Provided argument `prediction_matrix` is not a Numpy.Array object")

    prediction_df = pd.DataFrame(prediction_matrix[:,:(top_n)])
    prediction_df['targetId'] = movie_id

    columns = [c+1 for c in prediction_df.columns if c != "targetId"]
    prediction_df.columns = columns+['targetId']
    prediction_df = prediction_df[['targetId']+columns] # final predictions to be saved in RDS

    return prediction_df

def predict(corr, movie_id, config):
    """Perform all model prediction steps."""
    prediction_matrix = predict_matrix(corr, movie_id)
    predictions = predict_df(prediction_matrix, movie_id, **config['predict_df'])

    return predictions
