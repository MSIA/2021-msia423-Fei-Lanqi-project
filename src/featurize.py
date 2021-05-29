import logging 

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def get_avg_rating(ratings):
    """Get average rating for each movie."""

    avg_ratings = pd.DataFrame(ratings.groupby('movieId')['rating'].mean())

    return avg_ratings

def get_popularity(ratings):
    """Get view counts for each movie."""

    # filter out users with less than user_min ratings
    popularity = pd.DataFrame(ratings.groupby('movieId')['rating'].count())

    return popularity

def featurize(movies, ratings, feature_names):
    """Concatenate features and merge with movies."""

    agg_ratings = get_avg_rating(ratings); agg_ratings
    agg_ratings.rename(columns={'rating':feature_names[0]}, inplace=True)
    agg_ratings[feature_names[1]] = get_popularity(ratings)

    movies = agg_ratings.merge(movies, left_index=True, right_on="movieId")
    movies = movies[['movieId','doubanId','imdbId','title']+feature_names]

    return movies, ratings