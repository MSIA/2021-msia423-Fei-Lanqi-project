import logging 

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def predict_aux(dist_list, movieID):
    """
    Auxilliary function that takes a movie's distance array and returns an array of movie ids,
    ranked by each movie's similarity for the given movie.

    Args:
        dist_list (np.array) - the distance array for a movie
        movieID (np.array) - the list of movie IDs used in model training
    Returns:
        result (np.array) - the movie ID list, ranked by similarity to the input movie, excluding
        the input movie.
    """

    if len(dist_list) > len(movieID):
        logger.error("Provided `movieID` has smaller length than `dist_list`")
        raise IndexError("Provided `movieID` has smaller length than `dist_list`")

    result = np.argsort(-dist_list)
    result = [movieID[i] for i in result]
    result = np.array(result[1:]) # discard the most similar movie, which is itself

    return result

def predict_matrix(corr, movieID):
    """
    Get the predictions (the similar movies) in a matrix form.

    Args:
        corr (numpy.array) - the trained model object, correlation matrix from model training step
        movieID (numpy.array) - the list of movie IDs used in model training
    Returns:
        prediction matrix (numpy.array) - the predictions, each row is the result list (described in previous
        function) for a particular movie
    """

    if not isinstance(corr, np.ndarray):
        logger.error("Provided argument `corr` is not a Numpy.Array object")
        raise TypeError("Provided argument `corr` is not a Numpy.Array object")

    prediction_matrix = np.array([predict_aux(x, movieID) for x in corr]) 

    return prediction_matrix

def predict_df(prediction_matrix, movieID, top_n = 10):
    """
    Transform the prediction matrix into a pandas dataframe with appropriate indices.

    Args:
        prediction_matrix (numpy.array) - the prediction matrix from last step
        movieID (numpy.array) - the list of movie IDs used in model training
        top_n (int) - how many recommendations to be generated for each movie
    Returns:
        prediction_df (pandas.DataFrame) - the predictions matrix in pandas dataframe format
    """

    if not isinstance(prediction_matrix, np.ndarray):
        logger.error("Provided argument `prediction_matrix` is not a Numpy.Array object")
        raise TypeError("Provided argument `prediction_matrix` is not a Numpy.Array object")

    prediction_df = pd.DataFrame(prediction_matrix[:,:(top_n)])
    prediction_df['targetId'] = movieID

    columns = [c+1 for c in prediction_df.columns if c != "targetId"]
    prediction_df.columns = columns+['targetId']
    prediction_df = prediction_df[['targetId']+columns] # final predictions to be saved in RDS

    return prediction_df

def predict(corr, movieID, config):
    """Perform all model prediction steps."""

    prediction_matrix = predict_matrix(corr, movieID)
    predictions = predict_df(prediction_matrix, movieID, **config['predict_df'])

    return predictions