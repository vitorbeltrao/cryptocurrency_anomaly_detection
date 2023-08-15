'''
Unit tests for the functions included in
the "get_api_data.py" component

Author: Vitor Abdo
Date: Aug/2023
'''

# import necessary packages
from components.get_api_data import get_historical_data


def test_columns_get_historical_data_success(sample_api_data):
    '''Test whether get_historical_data returns correct data columns.'''
    ticker = 'ETH-USD'
    start_date = '2023-01-01'
    end_date = '2023-01-04'
    result = get_historical_data(ticker, start_date, end_date)

    assert all(col in sample_api_data.columns for col in result.columns)


def test_index_get_historical_data_success(sample_api_data):
    '''Test whether get_historical_data returns correct index.'''
    ticker = 'ETH-USD'
    start_date = '2023-01-01'
    end_date = '2023-01-04'
    result = get_historical_data(ticker, start_date, end_date)

    assert result.index.name == sample_api_data.index.name
