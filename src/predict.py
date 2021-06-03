import logging 

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def predict_aux(dist_list, movieID):
    """Auxilliary function that takes a movie's distance array and returns an array of movie ids."""
    
    result = np.argsort(-dist_list)
    result = [movieID[i] for i in result]

    return np.array(result[1:]) # discard the most similar movie, which is itself

def predict_matrix(corr, movieID):
    """Get the predictions (the similar movies) in a matrix form."""

    prediction_matrix = np.array([predict_aux(x, movieID) for x in corr]) 

    return prediction_matrix

def predict_df(prediction_matrix, movieID, top_n = 10):
    """Transform the predictions to dataframe format."""

    prediction_df = pd.DataFrame(prediction_matrix[:,:(top_n+1)])
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