

from src.train import get_rating_matrix, compute_distance
import pandas as pd
import numpy as np

# TEST TRAIN MODULE

def test_get_rating_matrix(): 
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
        [[5., 4., 3., 0., 0., 0.],
         [4., 0., 5., 0., 0., 0.],
         [5., 5., 4., 0., 2., 0.],
         [5., 0., 4., 0., 0., 0.],
         [0., 0., 0., 0., 0., 3.],
         [4., 0., 0., 5., 5., 0.],
         [4., 0., 2., 4., 0., 0.],
         [0., 0., 0., 4., 0., 0.],
         [0., 0., 0., 2., 0., 0.]],
        index=[0, 1, 2, 3, 4, 5, 6, 11, 17],
        columns=[0, 1, 2, 3, 4, 5])

    df_true.index.name = 'movieId'
    df_true.columns.name = 'userId'

    # Compute test output
    df_test = get_rating_matrix(df_in)[0]

    # Test that the true and test are the same
    pd._testing.assert_frame_equal(df_true, df_test)

def test_compute_distance():
    # Define input dataframe
    df_in = pd.DataFrame(
        [[5., 4., 3., 0., 0., 0.],
         [4., 0., 5., 0., 0., 0.],
         [5., 5., 4., 0., 2., 0.],
         [5., 0., 4., 0., 0., 0.],
         [0., 0., 0., 0., 0., 3.],
         [4., 0., 0., 5., 5., 0.],
         [4., 0., 2., 4., 0., 0.],
         [0., 0., 0., 4., 0., 0.],
         [0., 0., 0., 2., 0., 0.]],
        index=[0, 1, 2, 3, 4, 5, 6, 11, 17],
        columns=[0, 1, 2, 3, 4, 5])

    df_in.index.name = 'movieId'
    df_in.columns.name = 'userId'

    # Define expected output
    output_true = np.array([[1., 0.63576395, 0.93779311, 0.71055971, -0.42966892,
                             -0.27174649,  0.26761547, -0.42966892, -0.42966892],
       [0.63576395, 1., 0.58358932, 0.96363636, -0.31333978, -0.16514456, 0.47705996, 
        -0.31333978, -0.31333978],
       [0.93779311, 0.58358932, 1., 0.62006365, -0.55874424, -0.24294936, 0.05800148, 
        -0.55874424, -0.55874424],
       [0.71055971, 0.96363636, 0.62006365, 1., -0.31333978, -0.03302891, 0.56379814,
        -0.31333978, -0.31333978],
       [-0.42966892, -0.31333978, -0.55874424, -0.31333978, 1., -0.44271887, -0.4152274,
        -0.2, -0.2],
       [-0.27174649, -0.16514456, -0.24294936, -0.03302891, -0.44271887, 1., 0.49896444,
        0.50596443, 0.50596443],
       [0.26761547, 0.47705996, 0.05800148, 0.56379814, -0.4152274, 0.49896444, 1.,
        0.58131836, 0.58131836],
       [-0.42966892, -0.31333978, -0.55874424, -0.31333978, -0.2, 0.50596443, 0.58131836,
        1., 1.],
       [-0.42966892, -0.31333978, -0.55874424, -0.31333978, -0.2, 0.50596443, 0.58131836,
        1., 1.]])


    # Compute test output
    output_test = compute_distance(df_in)

    # Test that the true and test are the same
    np.testing.assert_almost_equal(output_test, output_true) # almost equal used because of floating point

