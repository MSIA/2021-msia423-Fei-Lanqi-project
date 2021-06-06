
import logging

import pandas as pd
import numpy as np
import botocore

logger = logging.getLogger(__name__)


def acquire(s3_path, file_name_movies, file_name_links, file_name_ratings):
    """
    Load the raw data from the s3 path and returns the pandas dataframe.

    Args:
        s3_path (str) - s3 path
        file_name_movies (str) - movies data file name
        file_name_links (str) - links data file name
        file_name_ratings (str) - ratings data file name

    Returns:
        movies (pandas.DataFrame) - movies dataframe
        links (pandas.DataFrame) - links dataframe
        ratings (pandas.DataFrame) - ratings dataframe
    """

    try:
        movies = pd.read_csv(s3_path+file_name_movies)
        links = pd.read_csv(s3_path+file_name_links)
        ratings = pd.read_csv(s3_path+file_name_ratings)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info("raw datasets are loaded to pandas dataframes.")

    return movies, links, ratings



    
