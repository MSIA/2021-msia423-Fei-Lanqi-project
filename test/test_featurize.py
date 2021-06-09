"""Test featurize module"""

import pytest
import pandas as pd

from src.featurize import get_avg_rating, get_popularity

def test_get_avg_rating():
    # Define input dataframe
    df_in_values = [[0, 0, 5, 1318222486], [0, 1, 4, 1313813583], [0, 2, 5, 1313458035],
                 [0, 3, 5, 1313327802], [0, 5, 4, 1307669511], [0, 6, 4, 1305861115],
                 [1, 7, 4, 1294659968], [1, 8, 5, 1294657417], [2, 9, 3, 1294547778],
                 [2, 10, 5, 1294547757], [2, 11, 4, 1292159777], [2, 12, 4, 1289795908],
                 [2, 13, 2, 1289795776], [3, 14, 5, 1288455663], [3, 15, 4, 1287644898],
                 [3, 16, 4, 1287644833], [3, 17, 2, 1287644790], [4, 18, 2, 1287644735],
                 [4, 19, 5, 1284393419], [5, 4, 3, 1312126734]]

    df_in_index = [*range(20)]

    df_in_columns = ['userId', 'movieId', 'rating', 'timestamp']

    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_columns)

    # Define expected output, df_true
    df_true = pd.DataFrame(
        [[5], [4], [5], [5], [3], [4], [4], [4], [5], [3], [5], [4], [4], [2], [5],
         [4], [4], [2], [2], [5]],
        index=df_in_index,
        columns=['rating'])

    df_true.index.name = 'movieId'

    # Compute test output
    df_test = get_avg_rating(df_in)

    # Test that the true and test are the same
    pd._testing.assert_frame_equal(df_true, df_test)

def test_get_avg_rating_nondf():
    df_in = 'I am not a dataframe'

    with pytest.raises(TypeError):
        get_avg_rating(df_in)

def test_get_popularity():
    # Define input dataframe
    df_in_values = [[0, 0, 5, 1318222486], [0, 1, 4, 1313813583], [0, 2, 5, 1313458035],
                 [0, 3, 5, 1313327802], [0, 5, 4, 1307669511], [0, 6, 4, 1305861115],
                 [1, 0, 4, 1294659968], [1, 2, 5, 1294657417], [2, 0, 3, 1294547778],
                 [2, 1, 5, 1294547757], [2, 2, 4, 1292159777], [2, 3, 4, 1289795908],
                 [2, 6, 2, 1289795776], [3, 5, 5, 1288455663], [3, 6, 4, 1287644898],
                 [3, 11, 4, 1287644833], [3, 17, 2, 1287644790], [4, 2, 2, 1287644735],
                 [4, 5, 5, 1284393419], [5, 4, 3, 1312126734]]

    df_in_index = [*range(20)]

    df_in_columns = ['userId', 'movieId', 'rating', 'timestamp']

    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_columns)

    # Define expected output, df_true
    df_true = pd.DataFrame(
        [[3], [2], [4], [2], [1], [3], [3], [1], [1]],
        index=[0, 1, 2, 3, 4, 5, 6, 11, 17],
        columns=['rating'])

    df_true.index.name = 'movieId'

    # Compute test output
    df_test = get_popularity(df_in)

    # Test that the true and test are the same
    pd._testing.assert_frame_equal(df_true, df_test)

def test_get_popularity_nondf():
    df_in = 'I am not a dataframe'

    with pytest.raises(TypeError):
        get_popularity(df_in)
