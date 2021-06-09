"""Feature engineering."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

# the features are not used in model, but used in app
# the model is CBF, so these aggregated features are not needed
def get_avg_rating(ratings):
    """
    Get average rating for each movie.

    Args:
        ratings (pandas.DataFrame) - cleaned ratings dataframe

    Returns:
        avg_ratings (pandas.DataFrame) - the aggregated ratings dataframe
    """
    if not isinstance(ratings, pd.DataFrame):
        logger.error("Provided argument `ratings` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `ratings` is not a Panda's DataFrame object")

    avg_ratings = pd.DataFrame(ratings.groupby('movieId')['rating'].mean()) # aggregate by user

    return avg_ratings

def get_popularity(ratings):
    """
    Get view counts (popularity) for each movie.

    Args:
        ratings (pandas.DataFrame) - cleaned ratings dataframe

    Returns:
        popularity (pandas.DataFrame) - the popularity dataframe
    """
    if not isinstance(ratings, pd.DataFrame):
        logger.error("Provided argument `ratings` is not a Panda's DataFrame object")
        raise TypeError("Provided argument `ratings` is not a Panda's DataFrame object")

    # filter out users with less than user_min ratings
    popularity = pd.DataFrame(ratings.groupby('movieId')['rating'].count())

    return popularity

def featurize(movies, ratings, feature_names):
    """
    Concatenate features and merge with movies.

    Args:
        movies (pandas.DataFrame) - cleaned movies dataframe
        ratings (pandas.DataFrame) - cleaned ratings dataframe
        feature_names (list) - the feature names, drawn from configurationg file

    Returns:
        ratings (pandas.DataFrame) - featurized ratings dataframe
    """
    agg_ratings = get_avg_rating(ratings)
    # rename column if a user gives a different one than default
    agg_ratings.rename(columns={'rating':feature_names[0]}, inplace=True)
    agg_ratings[feature_names[1]] = get_popularity(ratings)
    logger.info("Feature %s is generated", feature_names[0])

    movies = agg_ratings.merge(movies, left_index=True, right_on="movieId")
    movies = movies[['movieId','doubanId','imdbId','title']+feature_names]
    logger.info("Feature %s is generated", feature_names[1])

    return movies
