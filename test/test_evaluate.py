
import pytest
import pandas as pd
import numpy as np

from src.evaluate import get_fav_movies, get_most_similar_movie, get_score

def test_get_fav_movies():
    # Define inputs
    movieID = [0, 1, 2, 3, 4, 5, 6, 11, 17]
    userID = [0, 1, 2, 3, 4, 5]
    ratings_pivot = pd.DataFrame(
        [[5., 4., 3., 0., 0., 0.],
         [4., 0., 5., 0., 0., 0.],
         [5., 5., 4., 0., 2., 0.],
         [5., 0., 4., 0., 0., 0.],
         [0., 0., 0., 0., 0., 3.],
         [4., 0., 0., 5., 5., 0.],
         [4., 0., 2., 4., 0., 0.],
         [0., 0., 0., 4., 0., 0.],
         [0., 0., 0., 2., 0., 0.]],
        index=movieID,
        columns=userID)
    ratings_pivot.index.name = 'movieId'
    ratings_pivot.columns.name = 'userId'

    # Define true output
    df_true = pd.DataFrame([[0, 0], [2, 1], [1, 2], [5, 3], [5, 4], [4, 5]],
    index=[0, 1, 2, 3, 4, 5],
    columns=["fav_movie","userId"])

    # Compute test output
    df_test = get_fav_movies(ratings_pivot, movieID, userID)[0]

    # Test that the true and test are the same
    pd._testing.assert_frame_equal(df_true, df_test)

def test_get_fav_movies_nondf():
    df_in = 'I am not a dataframe'
    movieID = [0, 1, 2, 3, 4, 5, 6, 11, 17]
    userID = [0, 1, 2, 3, 4, 5]

    with pytest.raises(TypeError):
        get_fav_movies(df_in, movieID, userID)

def test_get_most_similar_movie():
    # Define inputs
    fav_movies = pd.DataFrame([[0, 0], [2, 1], [1, 2], [5, 3], [5, 4], [4, 5]],
    index=[0, 1, 2, 3, 4, 5], columns=["fav_movie","userId"])
    movieID = [0, 1, 2, 3, 4, 5, 6, 11, 17]
    corr = np.array([[1, 0.8, 0.2, 0.7, 0.4, 0.1, 0.33, 0.13, 0.45],
    [1, 0.23, 0.2, 0.07, 0.78, 0.4, 0.35, 0.83, 0.5],
    [1, 0.03, 0.1, 0.7, 0.4, 0.1, 0.44, 0.31, 0.42],
    [1, 0.32, 0.42, 0.37, 0.4, 0.09, 0.33, 0.13, 0.27],
    [1, 0.43, 0.2, 0.98, 0.29, 0.34, 0.23, 0.04, 0.18],
    [1, 0.3, 0.23, 0.67, 0.19, 0.1, 0.13, 0.41, 0.22],
    [1, 0.2, 0.54, 0.56, 0.08, 0.32, 0.41, 0.64, 0.31],
    [1, 0.65, 0.3, 0.34, 0.45, 0.33, 0.37, 0.3, 0.05],
    [1, 0.67, 0.05, 0.29, 0.24, 0.72, 0.33, 0.1, 0.53]])

    # Define true output
    df_true = pd.DataFrame([[ 0,  0,  1],
       [ 2,  1,  3],
       [ 1,  2, 11],
       [ 5,  3,  3],
       [ 5,  4,  3],
       [ 4,  5,  3]],
       index = [0, 1, 2, 3, 4, 5],
       columns=["fav_movie", "userId", "most_similar_to_fav"])

    # Compute test result
    df_test = get_most_similar_movie(fav_movies, movieID, corr)

    # Test that the true and test are the same
    pd._testing.assert_frame_equal(df_true, df_test)

def test_get_most_similar_movie_nondf():
    df_in = 'I am not a dataframe'
    movieID = [0, 1, 2, 3, 4, 5, 6, 11, 17]
    corr = np.array([[1, 0.8, 0.2, 0.7, 0.4, 0.1, 0.33, 0.13, 0.45],
    [1, 0.23, 0.2, 0.07, 0.78, 0.4, 0.35, 0.83, 0.5],
    [1, 0.03, 0.1, 0.7, 0.4, 0.1, 0.44, 0.31, 0.42],
    [1, 0.32, 0.42, 0.37, 0.4, 0.09, 0.33, 0.13, 0.27],
    [1, 0.43, 0.2, 0.98, 0.29, 0.34, 0.23, 0.04, 0.18],
    [1, 0.3, 0.23, 0.67, 0.19, 0.1, 0.13, 0.41, 0.22],
    [1, 0.2, 0.54, 0.56, 0.08, 0.32, 0.41, 0.64, 0.31],
    [1, 0.65, 0.3, 0.34, 0.45, 0.33, 0.37, 0.3, 0.05],
    [1, 0.67, 0.05, 0.29, 0.24, 0.72, 0.33, 0.1, 0.53]])

    with pytest.raises(TypeError):
        get_most_similar_movie(df_in, movieID, corr)

def test_get_score():
    # Define inputs
    ratings_pivot_t = pd.DataFrame(
        [[4.8, 4, 3, 0, 0, 0, 0, 0, 4.6, 0], # user 0
         [0, 3, 4.9, 0, 0, 4.3, 4.8, 0, 2.3, 0], # user 2
         [3.8, 0, 0, 4.2, 0, 0, 0, 3.6, 0, 0], # user 4
         [0, 0, 3.9, 0, 4.2, 4.9, 0, 0, 4.1, 0], # user 5
         [4, 4.6, 0, 0, 0, 3.7, 3.7, 0, 3.4, 4.1]], # user 8
        index=[0, 2, 4, 5, 8], # user ID
        columns=[2, 12, 15, 43, 101, 262, 461, 736, 1413, 1715]) # movie ID
    
    fav_movies = pd.DataFrame([[2, 0, 1413], [15, 2, 461], [43, 4, 1715], 
                               [262, 5, 736], [12, 8, 101]], 
                               index=[0, 1, 2, 3, 4], 
                               columns=["fav_movie", "userId", "most_similar_to_fav"])

    # Define true score
    score_true = (4.6 + 4.8)/2

    # Compute test output
    score_test = get_score(fav_movies, ratings_pivot_t)

    assert score_test == score_true

def test_get_score_nondf():
    df_in = 'I am not a dataframe'

    with pytest.raises(TypeError):
        get_score(df_in, df_in)