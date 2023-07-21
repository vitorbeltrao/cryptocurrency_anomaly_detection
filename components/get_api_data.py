'''
Script to extract data from Yahoo finance
API and read as a pandas dataframe

Author: Vitor Abdo
Date: July/2023
'''

# import necessary packages
import logging
import yfinance as yf
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def get_historical_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    '''
    Get historical price data from Yahoo Finance.

    Args:
        ticker (str): The ticker symbol of the cryptocurrency (e.g., 'ETH-USD').
        start_date (str): Start date in the format 'YYYY-MM-DD'.
        end_date (str): End date in the format 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: DataFrame containing historical price data.
    '''
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        logging.info(f'The historical dataframe for {ticker} were fetched successfully.')
        return data
    
    except Exception as e:
        logging.error(f'Error fetching data: {e}.')
        return pd.DataFrame()


df = get_historical_data('ETH-USD', '2023-01-01', '2023-07-21')
print(df)