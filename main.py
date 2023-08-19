'''
Script to manage all functions

Author: Vitor Abdo
Date: Aug/2023
'''

# import necessary packages
import logging
import datetime
import pandas as pd
import numpy as np
from decouple import config

from components.get_api_data import get_historical_data
from components.create_s3_raw import move_files_to_raw_layer
from components.create_s3_processed import move_files_to_processed_layer, get_files_from_processed_layer
from components.dw_management import create_schema_into_postgresql
from components.dw_management import create_table_into_postgresql
from components.dw_management import insert_data_into_postgresql
from components.dw_management import fetch_data_from_database
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

FROM = config('FROM')
TO = config('TO')
EMAIL_PASS = config('PASS')


if __name__ == "__main__":
    # Define the start and end date of the period of interest to collect API data
    today_date = datetime.datetime.now()
    yesterday_date = today_date - datetime.timedelta(days=1)

    # 1. Get the raw data from API
    logging.info('About to start getting data from the yahoo API')
    raw_df = get_historical_data(TICKER, yesterday_date.date(), today_date.date())

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
    id INT,
    date TEXT,
    price_amplitude FLOAT,
    created_at TEXT,
    updated_at TEXT,
    PRIMARY KEY (date)
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

    # 8. anomaly detection
    conn_string = f'host={ENDPOINT_NAME} port={PORT} dbname={DB_NAME} user={USER} password={PASSWORD}'
    query = '''
    SELECT * FROM cryptocurrency.processed_eth_historical_data
    '''
    anomaly_df = fetch_data_from_database(conn_string, query)
    logging.info(f'The dataframe about {TICKER} cryptocurrency was fetched successfully.')

    anomaly_df['date'] = pd.to_datetime(anomaly_df['date'])
    anomaly_df.sort_values(by=['date'], inplace=True)

    # get the last value from yesterday about ETH cryptocurrency to test the anomaly
    last_crypto_value = round(anomaly_df['price_amplitude'].iloc[-1], 2)
    logging.info(f'The last value from yesterday {last_crypto_value} was fetched successfully.')

    # get the entire distribution to compare the last value
    data_distribution = anomaly_df['price_amplitude'].iloc[:-1].values
    data_distribution = [round(value, 2) for value in data_distribution]
    logging.info(f'The data distribution from the historic data for {TICKER} were fetched successfully.')

    # Perform outlier elimination
    anomaly_transformer = AnomalyTransformer(data_distribution)
    anomaly_transformer.fit_transform()
    transformed_data = anomaly_transformer.transformed_data
    logging.info(f'The outliers were eliminated from historic data distribution.')

    # calculate mean, standard deviation, and threshold about cleaned distribution
    mean_transformed = np.mean(transformed_data)
    std_transformed = np.std(transformed_data)
    threshold_transformed = 3 * std_transformed

    # create anomaly detector
    anomaly_detector = AnomalyDetector(
        transformed_data, mean_transformed, std_transformed, threshold_transformed)
    
    # perform anomaly detection
    if anomaly_detector.is_anomaly(last_crypto_value):
        p_value = anomaly_detector.anomaly_report(last_crypto_value) # Generate anomaly report

        email_subject = f'Anomaly about {TICKER} cryptocurrency has been found!'
        email_body = f'The anomaly detection system found an anomaly with a value of {last_crypto_value} and a p-value of {p_value}'
        send_gmail_message(FROM, TO, EMAIL_PASS, email_subject, email_body)

    logging.info(
        f'The anomaly detection system for day {today_date.date()} ran successfully for the quote value {last_crypto_value} obtained for yesterday day {yesterday_date.date()}')
