
import pytest
import pandas as pd
import numpy as np

from src.clean import merge_data, filter

# TEST CLEAN MODULE

def test_merge_data(): 
    # Define input dataframe
    df_in_movies = [[0, np.nan], [1, 'Harry Potter and the Deathly Hallows: Part II'],
       [2, 'Oceans'], [3, np.nan], [4, 'Transformers 3：Amphimixis At The End Of  The World']]

    df_in_index = [*range(5)]

    df_in_movies_columns = ['movieId', 'title']

    df_in_movies = pd.DataFrame(df_in_movies, index=df_in_index, columns=df_in_movies_columns)

    df_in_links = [[0, np.nan, 6.395463e+06], [1, 1.201607e+06, 3.011235e+06],
       [2, 7.651280e+05, 3.443389e+06], [3, np.nan, 6.778368e+06],
       [4, 1.399103e+06, 3.610047e+06]]

    df_in_links_columns = ['movieId', 'imdbId', 'doubanId']

    df_in_links = pd.DataFrame(df_in_links, index=df_in_index, columns=df_in_links_columns)

    # Define expected output, df_true
    df_true = pd.DataFrame(
        [[0, np.nan, 6395463.0, np.nan], [1, 1201607.0, 3011235.0,
        'Harry Potter and the Deathly Hallows: Part II'],
         [2, 765128.0, 3443389.0, 'Oceans'], [3, np.nan, 6778368.0, np.nan],
         [4, 1399103.0, 3610047.0, 'Transformers 3：Amphimixis At The End Of  The World']],
        index=[*range(5)],
        columns=df_in_links_columns+['title'])

    # Compute test output
    df_test = merge_data(df_in_movies, df_in_links)

    # Test that the true and test are the same
    pd._testing.assert_frame_equal(df_true, df_test)

def test_merge_nondf():
    df_in = 'I am not a dataframe'

    with pytest.raises(TypeError):
        merge_data(df_in, df_in)

def test_filter():
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
        [[0, 0, 5, 1318222486], [0, 1, 4, 1313813583], [0, 2, 5, 1313458035],
        [0, 3, 5, 1313327802], [0, 5, 4, 1307669511], [0, 6, 4, 1305861115],
        [2, 9, 3, 1294547778], [2, 10, 5, 1294547757], [2, 11, 4, 1292159777], 
        [2, 12, 4, 1289795908], [2, 13, 2, 1289795776]],
        index=[0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12],
        columns=df_in_columns)

    # Compute test output

    df_test = filter(df_in, user_min=5, movie_min=1)

    # Test that the true and test are the same
    pd._testing.assert_frame_equal(df_true, df_test)

def test_filter_nondf():
    df_in = 'I am not a dataframe'

    with pytest.raises(TypeError):
        merge_data(df_in, user_min=5, movie_min=1)