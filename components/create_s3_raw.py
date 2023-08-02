'''
Script to move data arrived from 
Yahoo Finance to AWS S3 raw layer

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


def move_files_to_raw_layer(
        bucket_name: str, 
        aws_access_key_id: str, 
        aws_secret_access_key: str, 
        region_name: str,
        input_df: pd.DataFrame) -> None:
    '''
    Move that we fetched from Yahoo API to the raw layer folder in AWS S3.

    :param bucket_name: (str) Name of the S3 bucket.
    :param aws_access_key_id: (str) AWS access key ID.
    :param aws_secret_access_key: (str) AWS secret access key.
    :param region_name: (str) AWS region name.
    :param input_df: (dataframe) pandas dataframe that you want to upload in raw layer.
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

    # Define the start and end date of the period of interest (last day)
    today_date = datetime.datetime.now()

    # Define the destination directory path with the current date
    destination_directory = f'raw/crypto_anomaly_detect/eth/extracted_at={today_date.date()}/eth_historical_data.csv'

    # Read the raw data from yahoo finance api
    eth_df = input_df
    logging.info('The ETH dataframe from yesterday was fetched successfully.')

    # Create the 'tmp' directory if it doesn't exist
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    # Save the processed data to csv format
    eth_df.to_csv(f'/tmp/{today_date.date()}_eth_historical_data.csv')

    # Upload the csv file to S3
    s3_client.upload_file(f'/tmp/{today_date.date()}_eth_historical_data.csv', bucket_name, destination_directory)

    # Delete the temporary file
    os.remove(f'/tmp/{today_date.date()}_eth_historical_data.csv')
    logging.info(f'Raw data for {today_date.date()} was uploaded and saved in {destination_directory}.')
