'''
Unit tests for the functions included in
the "anomaly_detection_system.py" component

Author: Vitor Abdo
Date: Aug/2023
'''

# import necessary packages
import pytest
import numpy as np
from scipy import stats
from components.anomaly_detection_system import detect_outliers_iqr, AnomalyTransformer

# DETERMINISTIC TESTS
@pytest.mark.parametrize("data, k, return_thresholds, expected_result", [
    # Test case 1: Basic test
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1.5, False, np.array([False, False, False, False, False, False, False, False, False, False])),

    # Test case 2: Data with outliers
    ([1, 2, 3, 4, 5, 20, 6, 7, 8, 30], 1.5, False, np.array([False, False, False, False, False, True, False, False, False, True])),

    # Test case 3: Data with different outlier cutoff
    ([1, 2, 3, 4, 5, 20, 6, 7, 8, 30], 2.0, False, np.array([False, False, False, False, False, True, False, False, False, True])),

    # Test case 4: Return thresholds
    ([1, 2, 3, 4, 5, 20, 6, 7, 8, 30], 1.5, True, (-3.5, 14.5)),

    # Test case 5: Empty data
    ([np.nan, np.nan, np.nan], 1.5, False, np.array([False, False, False])),

    # Test case 6: Data with only one element
    ([42], 1.5, False, np.array([False])),
])


def test_detect_outliers_iqr(data, k, return_thresholds, expected_result):
    '''Unit tests for detect_outliers_iqr func in anomaly_detection_system component'''
    result = detect_outliers_iqr(data, k, return_thresholds)
    assert np.array_equal(result, expected_result)


def test_anomaly_detector_is_anomaly(anomaly_detector):
    '''Unit tests for detect_outliers_iqr func in anomaly_detection_system component'''
    # Test case 1: Value within the threshold
    value1 = 1.5
    assert not anomaly_detector.is_anomaly(value1)

    # Test case 2: Value above the threshold
    value2 = 15.3
    assert anomaly_detector.is_anomaly(value2)

    # Test case 3: Value below the threshold
    value3 = -4.58
    assert anomaly_detector.is_anomaly(value3)


# NON-DETERMINISTIC TESTS
def test_normality_db_data(historical_amplitude):
    '''Non deterministic tests for our historical data stored in database
    that verify if our data without outliers follow normal distribuition
    '''
    # Perform outlier elimination
    data_distribution = historical_amplitude['price_amplitude'].values
    anomaly_transformer = AnomalyTransformer(data_distribution)
    anomaly_transformer.fit_transform()
    transformed_data = anomaly_transformer.transformed_data

    # test with shapiro test
    alpha = 0.05  # significance level
    shapiro = stats.shapiro(transformed_data)

    assert shapiro[1] > alpha
