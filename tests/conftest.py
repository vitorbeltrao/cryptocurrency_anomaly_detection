'''
This .py file is for creating the fixtures

Author: Vitor Abdo
Date: Aug/2023
'''

# import necessary packages
import pytest
import os
import pandas as pd
import numpy as np
from components.dw_management import fetch_data_from_database
from components.anomaly_detection_system import AnomalyDetector

# config
ENDPOINT_NAME = os.getenv('ENDPOINT_NAME')
PORT = os.getenv('PORT')
DB_NAME = os.getenv('DB_NAME')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')

@pytest.fixture
def sample_api_data():
    data = {
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
        'Open': [100, 105, 110, 115],
        'High': [102, 107, 112, 117],
        'Low': [98, 103, 108, 113],
        'Close': [101, 106, 111, 116],
        'Adj Close': [101, 106, 111, 116],
        'Volume': [10000, 15000, 20000, 25000]
    }

    df_sample_api = pd.DataFrame(data)
    df_sample_api = df_sample_api.set_index('Date')
    
    return df_sample_api


@pytest.fixture
def anomaly_detector():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    mean = np.mean(data)
    std = np.std(data)
    threshold = 3 * std

    return AnomalyDetector(data, mean, std, threshold)


@pytest.fixture
def historical_amplitude():
    conn_string = f'host={ENDPOINT_NAME} port={PORT} dbname={DB_NAME} user={USER} password={PASSWORD}'
    query = '''
    SELECT * FROM cryptocurrency.processed_eth_historical_data
    '''
    historical_df = fetch_data_from_database(conn_string, query)

    return historical_df
