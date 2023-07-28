'''
Component to develop functions related to anomaly detection

Author: Vitor Beltrão
Data: July/2023
'''

# import necessary packages
import numpy as np
from scipy import stats


def detect_outliers_iqr(data: np.array, k=1.5, return_thresholds=False) -> np.array:
    '''
    Detect outliers in a dataset using the interquartile range (IQR) method.

    Parameters:
        data (array-like): Input data to detect outliers from.
        k (float): Multiplier to control the outlier cutoff (default: 1.5).
        return_thresholds (bool): Whether to return the lower and upper bounds (default: False).

    Returns:
        outliers (array-like or tuple): Boolean mask of outliers or lower and upper bounds.
    '''
    # Calculate quartiles
    q25, q75 = np.percentile(data, [25, 75])

    # Calculate the IQR
    iqr = q75 - q25

    # Calculate the outlier cutoff
    cutoff = iqr * k

    # Calculate the lower and upper bounds
    lower_bound, upper_bound = q25 - cutoff, q75 + cutoff

    if return_thresholds:
        return lower_bound, upper_bound
    else:
        # Identify outliers
        outliers = np.logical_or(data < lower_bound, data > upper_bound)
        return outliers


class AnomalyTransformer:
    def __init__(self, data: np.array):
        '''
        AnomalyTransformer class for outlier elimination.

        Parameters:
            data (array-like): Input data to be transformed.
        '''
        self.data = data
        self.transformed_data = None

    def fit_transform(self) -> np.array:
        '''
        Fit the data and transform it using outlier elimination.
        '''
        # Eliminate outliers
        outliers = detect_outliers_iqr(self.data)
        data_with_nan = np.where(outliers, np.nan, self.data)
        data_without_nan = data_with_nan[~np.isnan(data_with_nan)]

        # Transformed data
        self.transformed_data = data_without_nan


class AnomalyDetector:
    def __init__(self, transformed_data: np.array, mean: float, std: float, threshold: float):
        '''
        AnomalyDetector class for detecting anomalies based on transformed data and
        generate final reports to help decision making.

        Parameters:
            transformed_data (array-like): Transformed data for anomaly detection.
            mean (float): Mean of the transformed data.
            std (float): Standard deviation of the transformed data.
            threshold (float): Threshold for anomaly detection.
        '''
        self.transformed_data = transformed_data
        self.mean = mean
        self.std = std
        self.threshold = threshold

    def is_anomaly(self, value: float) -> bool:
        '''
        Check if a value is an anomaly based on the mean, standard deviation, and threshold.

        Parameters:
            value (float): The value to be checked.

        Returns:
            is_anomaly (bool): True if the value is an anomaly, False otherwise.
        '''
        if value > (
            self.mean + self.threshold) or value < (self.mean - self.threshold):
            return True
        else:
            return False
        
    def anomaly_report(self, value: float) -> float:
        '''
        Generate a report to measure a specific value: p-value.

        Parameters:
            value (float): The value to generate the report for.

        Returns:
            p_value (float): The p-value of statistic test.
        '''
        # Calculate p-value
        z_score = (value - self.mean) / self.std
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        return p_value
