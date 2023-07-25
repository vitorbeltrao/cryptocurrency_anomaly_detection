'''
Script to get data from datalake processed layer for redshift

Author: Vitor Abdo
Date: July/2023
'''

# import necessary packages
import logging
import psycopg2
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def create_redshift_table(
        redshift_host: str,
        redshift_port: str,
        redshift_database: str,
        redshift_user: str,
        redshift_password: str,
        table_name: str,
        column_definitions: list) -> None:
    '''
    Create a table in Amazon Redshift if it doesn't exist.

    Args:
        redshift_host (str): Hostname or IP address of the Redshift cluster.
        redshift_port (str): Port number for the Redshift connection.
        redshift_database (str): Name of the Redshift database.
        redshift_user (str): Username for the Redshift connection.
        redshift_password (str): Password for the Redshift connection.
        table_name (str): Name of the table to be created.
        column_definitions (list): List of dictionaries defining the columns and their data types.

    Returns:
        None
    '''
    # Establish a connection to Redshift
    conn = psycopg2.connect(
        host=redshift_host,
        port=redshift_port,
        database=redshift_database,
        user=redshift_user,
        password=redshift_password
    )

    # Check if the table already exists
    with conn.cursor() as cursor:
        cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (table_name,))
        table_exists = cursor.fetchone()[0]

        # Create the table if it doesn't exist
        if not table_exists:
            create_table_query = f"CREATE TABLE {table_name} ("
            for i, column in enumerate(column_definitions):
                column_name = column['name']
                column_type = column['type']
                create_table_query += f"{column_name} {column_type}"
                if i < len(column_definitions) - 1:
                    create_table_query += ","
            create_table_query += ")"
            cursor.execute(create_table_query)
            conn.commit()
            logging.info(f"Table '{table_name}' created in Redshift.")
        else:
            logging.info(f"Table '{table_name}' already exists in Redshift. Skipping table creation.")

    # Close the connection to Redshift
    conn.close()


def copy_data_from_s3_to_redshift(
        redshift_host: str,
        redshift_port: str,
        redshift_database: str,
        redshift_user: str,
        redshift_password: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        s3_bucket: str,
        s3_prefix: str,
        table_name: str) -> None:
    '''
    Copy data from a folder in Amazon S3 to a table in Amazon Redshift using the COPY command.

    Args:
        redshift_host (str): Hostname or IP address of the Redshift cluster.
        redshift_port (str): Port number for the Redshift connection.
        redshift_database (str): Name of the Redshift database.
        redshift_user (str): Username for the Redshift connection.
        redshift_password (str): Password for the Redshift connection.
        aws_access_key_id (str): AWS access key ID.
        aws_secret_access_key (str): AWS secret access key.
        s3_bucket (str): Name of the S3 bucket where the data is located.
        s3_prefix (str): Prefix of the S3 object key for the data.
        table_name (str): Name of the table in Redshift where the data will be loaded.

    Returns:
        None
    '''
    # Construct the S3 file path
    s3_path = f's3://{s3_bucket}/{s3_prefix}'

    # Construct the COPY command
    copy_command = f'''
    COPY {table_name}
    FROM '{s3_path}'
    CREDENTIALS 'aws_access_key_id={aws_access_key_id};aws_secret_access_key={aws_secret_access_key}'
    FORMAT AS PARQUET
    '''

    # Establish a connection to Redshift
    conn = psycopg2.connect(
        host=redshift_host,
        port=redshift_port,
        database=redshift_database,
        user=redshift_user,
        password=redshift_password
    )

    # Execute the COPY command
    with conn.cursor() as cursor:
        cursor.execute(copy_command)
        logging.info(f"Data copied from S3 to Redshift table '{table_name}'.")

    # Commit the changes
    conn.commit()

    # Close the connection to Redshift
    conn.close()


def fetch_data_from_redshift(redshift_host: str, redshift_port: str, redshift_database: str,
                             redshift_user: str, redshift_password: str, query: str) -> pd.DataFrame:
    '''
    Fetches data from an Amazon Redshift cluster using the provided connection details and query.

    Parameters:
        redshift_host (str): Redshift cluster endpoint.
        redshift_port (str): Redshift cluster port.
        redshift_database (str): Redshift database name.
        redshift_user (str): Redshift database user.
        redshift_password (str): Redshift database password.
        query (str): SQL query to fetch the data.

    Returns:
        DataFrame: A DataFrame containing the fetched data.
    '''
    conn = None 

    try:
        # Connect to the Redshift cluster
        conn = psycopg2.connect(
            host=redshift_host,
            port=redshift_port,
            database=redshift_database,
            user=redshift_user,
            password=redshift_password
        )

        # Fetch the data using the query
        logging.info('Fetching data from Amazon Redshift...')
        data = pd.read_sql(query, conn)

    except Exception as e:
        logging.error(f'Error fetching data from Amazon Redshift: {str(e)}')
        raise
    finally:
        # Close the connection if it was successfully established
        if conn is not None:
            conn.close()

    return data
