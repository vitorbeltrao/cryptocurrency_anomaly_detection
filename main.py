'''
Script to manage all functions

Author: Vitor Abdo
Date: Aug/2023
'''

# import necessary packages
import logging
import datetime
import boto3
from decouple import config

from components.get_api_data import get_historical_data
from components.create_s3_raw import move_files_to_raw_layer
from components.create_s3_processed import move_files_to_processed_layer
from components.dw_management import create_redshift_table
from components.dw_management import copy_data_from_s3_to_redshift
from components.dw_management import fetch_data_from_redshift
from components.anomaly_detection_system import detect_outliers_iqr
from components.anomaly_detection_system import AnomalyTransformer
from components.anomaly_detection_system import AnomalyDetector
from components.alert_system import send_gmail_message

logging.basicConfig(
    level=logging.INFO,
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

# config
TICKER = 'ETH-USD'

BUCKET_NAME = config('BUCKET_NAME')
AWS_ACCESSKEYID = config('AWS_ACCESSKEYID')
AWS_SECRETACCESSKEY = config('AWS_SECRETACCESSKEY')
REGION_NAME = config('REGION_NAME')

REDSHIFT_HOST = config('REDSHIFT_HOST')
REDSHIFT_PORT = config('REDSHIFT_PORT')
REDSHIFT_DB = config('REDSHIFT_DB')
REDSHIFT_USER = config('REDSHIFT_USER')
REDSHIFT_PASS = config('REDSHIFT_PASS')
REDSHIFT_TABLE_NAME = config('REDSHIFT_TABLE_NAME')


if __name__ == "__main__":
    # Define the start and end date of the period of interest to collect API data
    today_date = datetime.datetime.now()
    last_week_date = today_date - datetime.timedelta(days=7)

    # 1. Get the raw data from API
    raw_df = get_historical_data(TICKER, last_week_date, today_date)

    # 2. Send the raw df to s3 bucket raw layer
    move_files_to_raw_layer(BUCKET_NAME, AWS_ACCESSKEYID, AWS_SECRETACCESSKEY, REGION_NAME, raw_df)

    # 3. Move file to processed layer doing some transformations
    move_files_to_processed_layer(BUCKET_NAME, AWS_ACCESSKEYID, AWS_SECRETACCESSKEY, REGION_NAME)

    # 4. Create redshift table
    logging.info(
        f'About to start executing the create table {REDSHIFT_TABLE_NAME} function')
    table_columns = '''
    Date TEXT,
    price_amplitude FLOAT
    '''
    create_redshift_table(REDSHIFT_HOST, REDSHIFT_PORT, REDSHIFT_DB, REDSHIFT_USER, 
                          REDSHIFT_PASS, REDSHIFT_TABLE_NAME, table_columns)