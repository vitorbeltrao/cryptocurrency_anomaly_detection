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
from components.create_s3_processed import move_files_to_processed_layer, get_files_from_processed_layer
from components.dw_management import create_schema_into_postgresql
from components.dw_management import create_table_into_postgresql
from components.dw_management import insert_data_into_postgresql
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

ENDPOINT_NAME = config('ENDPOINT_NAME')
PORT = config('PORT')
DB_NAME = config('DB_NAME')
USER = config('USER')
PASSWORD = config('PASSWORD')
DW_SCHEMA_TO_CREATE = config('DW_SCHEMA_TO_CREATE')
DW_TEMP_SCHEMA_TO_CREATE = config('DW_TEMP_SCHEMA_TO_CREATE')
PROCESSED_TABLE_NAME = config('PROCESSED_TABLE_NAME')


if __name__ == "__main__":
    # Define the start and end date of the period of interest to collect API data
    today_date = datetime.datetime.now()
    last_week_date = today_date - datetime.timedelta(days=7)

    # 1. Get the raw data from API
    logging.info('About to start getting data from the yahoo API')
    raw_df = get_historical_data(TICKER, last_week_date, today_date)

    # 2. Send the raw df to s3 bucket raw layer
    logging.info('About to start the creation of raw layer')
    move_files_to_raw_layer(BUCKET_NAME, AWS_ACCESSKEYID, AWS_SECRETACCESSKEY, REGION_NAME, raw_df)

    # 3. Move file to processed layer doing some transformations
    logging.info('About to start the creation of processed layer')
    move_files_to_processed_layer(BUCKET_NAME, AWS_ACCESSKEYID, AWS_SECRETACCESSKEY, REGION_NAME)

    # 4. Get the current processed data
    logging.info('About to start getting data from processed layer')
    processed_data = get_files_from_processed_layer(BUCKET_NAME, AWS_ACCESSKEYID, AWS_SECRETACCESSKEY, REGION_NAME)
    logging.info('The processed data was fetched successfully')

    # 5. create rds schema if it does not already exist
    logging.info(f'About to start executing the create schema {DW_SCHEMA_TO_CREATE} function')
    create_schema_into_postgresql(ENDPOINT_NAME, PORT, DB_NAME, USER, PASSWORD, DW_SCHEMA_TO_CREATE) # main schema

    logging.info(f'About to start executing the create schema {DW_TEMP_SCHEMA_TO_CREATE} function')
    create_schema_into_postgresql(ENDPOINT_NAME, PORT, DB_NAME, USER, PASSWORD, DW_TEMP_SCHEMA_TO_CREATE) # temp schema

    # 6. Create rds table
    logging.info(f'About to start executing the create table {PROCESSED_TABLE_NAME} function')
    table_columns = '''
    date TEXT,
    price_amplitude FLOAT
    '''
    create_table_into_postgresql(
        ENDPOINT_NAME,
        PORT,
        DB_NAME,
        USER,
        PASSWORD,
        DW_SCHEMA_TO_CREATE,
        PROCESSED_TABLE_NAME,
        table_columns)
    
    # 7. insert data
    logging.info('About to start inserting data in our rds postgres table')
    if processed_data.empty:
        logging.info('The dataframe is empty.')

    else:
        insert_data_into_postgresql(
            ENDPOINT_NAME,
            PORT,
            DB_NAME,
            USER,
            PASSWORD,
            DW_SCHEMA_TO_CREATE,
            PROCESSED_TABLE_NAME,
            processed_data,
            DW_TEMP_SCHEMA_TO_CREATE)
