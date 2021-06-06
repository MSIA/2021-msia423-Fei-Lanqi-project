import pytest
import pandas as pd
import numpy as np

from src.predict import predict_aux, predict_matrix, predict_df

def test_predict_aux():
    # Define input lists
    distance_list = np.array([1, 0.43, 0.38, 0.59, 0.21, 0.33, 0.12, 0.02])
    movieID = np.array([1, 2, 3, 5, 6, 8, 14, 15])

    # Define true output
    output_true = np.array([5, 2, 3, 8, 6, 14, 15])

    # Compute test result
    output_test = predict_aux(distance_list, movieID)

    # Test that the true and test are the same
    np.testing.assert_array_equal(output_test, output_true)

def test_predict_aux_unhappy():
    # Define input lists
    distance_list = np.array([1, 0.43, 0.38, 0.59, 0.21, 0.33, 0.12, 0.02])
    movieID = np.array([1, 2, 3, 5, 6, 8, 14])

    with pytest.raises(IndexError):
        predict_aux(distance_list, movieID)

def test_predict_matrix():
    # Define inputs
    corr = np.array([[1., 0.63576395, 0.93779311, 0.71055971, -0.42966892],
                     [0.63576395, 1., 0.58358932, 0.96363636, -0.31333978],
                     [0.93779311, 0.58358932, 1., 0.62006365, -0.55874424],
                     [0.71055971, 0.96363636, 0.62006365, 1., -0.31333978],
                     [-0.42966892, -0.31333978, -0.55874424, -0.31, 1.]])
    movieID = [1, 2, 3, 5, 8]

    # Define true output
    output_true = [[3, 5, 2, 8], [5, 1, 3, 8], [1, 5, 2, 8], [2, 1, 3, 8], [5, 2, 1, 3]]

    # Compute test result
    output_test = predict_matrix(corr, movieID)

    # Test that the true and test are the same
    np.testing.assert_array_equal(output_test, output_true)

def test_predict_matrix_nonarray():
    corr = 'I am not a numpy array'
    movieID = [1, 2, 3, 5, 8]

    with pytest.raises(TypeError):
        predict_matrix(corr, movieID)

def test_predict_df():
    # Define inputs
    pred_matrix = np.array([[3, 5, 2, 8], 
                   [5, 1, 3, 8], 
                   [1, 5, 2, 8], 
                   [2, 1, 3, 8], 
                   [5, 2, 1, 3]])
    movieID = np.array([1, 2, 3, 5, 8])

    # Define true output 
    df_true = pd.DataFrame([[1, 3, 5, 2], [2, 5, 1, 3], [3, 1, 5, 2],
                            [5, 2, 1, 3],[8, 5, 2, 1]],
                            index=[0, 1, 2, 3, 4],
                            columns=['targetId', 1, 2, 3])
    
    # Compute test result
    df_test = predict_df(pred_matrix, movieID, top_n = 3)

    # Test that the true and test are the same
    np.testing.assert_array_equal(df_test, df_true)

def test_predict_df_nonarray():
    pred_matrix = 'I am not a numpy array'
    movieID = [1, 2, 3, 5, 8]

    with pytest.raises(TypeError):
        predict_df(pred_matrix, movieID, top_n = 3)
