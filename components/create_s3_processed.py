'''
Script to move data arrived from
s3 raw layer to s3 processed layer

Author: Vitor Abdo
Date: July/2023
'''

# import necessary packages
import boto3
import logging
import datetime
import os
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def move_files_to_processed_layer(
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str) -> None:
    '''
    Process data for the current day from raw layer and save it in the processed layer of the data lake.

    :param bucket_name: (str) Name of the S3 bucket.
    :param aws_access_key_id: (str) AWS access key ID.
    :param aws_secret_access_key: (str) AWS secret access key.
    :param region_name: (str) AWS region name.
    '''
    # Create a session with AWS credentials
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    # Create a client instance for S3
    s3_client = session.client('s3')
    logging.info('S3 authentication was created successfully.')

    # Get the current date
    today_date = datetime.datetime.now()

    # Define the paths for the raw and processed layers
    raw_directory = f'raw/crypto_anomaly_detect/eth/extracted_at={today_date.date()}/eth_historical_data.csv'
    processed_directory = f'processed/crypto_anomaly_detect/eth/extracted_at={today_date.date()}/processed_eth_historical_data.csv'

    # Read the raw data from S3, selecting only desired columns
    obj = s3_client.get_object(Bucket=bucket_name, Key=raw_directory)
    raw_data = pd.read_csv(obj['Body'], names=['Open', 'High', 'Low', 'Close', 'Adj Close', 
                                               'Volume'])
    logging.info('Raw data from s3 raw folder was fetched successfully.')

    ######################### Perform data transformations #########################
    processed_data = raw_data.copy()
    processed_data = processed_data[['Open', 'Close']] # select only necessary columns
    processed_data['price_amplitude'] = (processed_data['Close'] - processed_data['Open']) # create new column to perform the anomaly detection
    processed_data = processed_data[['price_amplitude']].reset_index()
    logging.info('Data transformation has been performed successfully.')

    ####################################################################################################
    # Create the 'tmp' directory if it doesn't exist
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    # Save the processed data to Parquet format
    processed_data.to_parquet(f'/tmp/{today_date.date()}_processed_eth_historical_data.parquet', compression='gzip')

    # Upload the Parquet file to S3
    s3_client.upload_file(f'/tmp/{today_date.date()}_processed_eth_historical_data.parquet', bucket_name, processed_directory)

    # Delete the temporary file
    os.remove(f'/tmp/{today_date.date()}_processed_eth_historical_data.parquet')
    logging.info(f'Processed data for {today_date.date()} processed and saved in {processed_directory}.')
