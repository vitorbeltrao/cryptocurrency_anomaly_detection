'''
File to create the schemas, tables and populate
them inside my postgres database

Author: Vitor Abdo
Date: May/2023
'''

# import necessary packages
import logging
import psycopg2
import pandas as pd
from sqlalchemy import create_engine, inspect

logging.basicConfig(
    level=logging.INFO,
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s')


def create_schema_into_postgresql(
        endpoint_name: str,
        port: int,
        db_name: str,
        user_name: str,
        password: str,
        schema_name: str) -> None:
    '''Connects to a PostgreSQL database on Amazon RDS and creates a schema if it does not already exist

    :param endpoint_name: (str)
    The endpoint URL of your Amazon RDS instance

    :param port: (int)
    The port number to connect to the database

    :param db_name: (str)
    The name of the database to connect to

    :param user_name: (str)
    The name of the user to authenticate as

    :param password: (str)
    The user's password

    :param schema_name: (str)
    The name of the schema to create
    '''

    # Set up the connection
    conn = psycopg2.connect(
        host=endpoint_name,
        port=port,
        database=db_name,
        user=user_name,
        password=password
    )

    # Create a cursor to execute SQL commands
    cur = conn.cursor()

    # Execute a query to check if the schema already exists
    cur.execute(
        f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema_name}'")
    result = cur.fetchone()

    # If the schema does not exist, create it
    if not result:
        cur.execute(f"CREATE SCHEMA {schema_name}")
        logging.info(f"Schema {schema_name} created successfully")
    else:
        logging.info(f"Schema {schema_name} already exists")

    # Commit and close the connection
    conn.commit()
    cur.close()
    conn.close()


def create_table_into_postgresql(
        endpoint_name: str,
        port: int,
        db_name: str,
        user_name: str,
        password: str,
        schema_name: str,
        table_name: str,
        table_columns: str) -> None:
    '''Function that creates a table if it does not exist in a PostgresSQL schema

    :param endpoint_name: (str)
    The endpoint URL of your Amazon RDS instance

    :param port: (int)
    The port number to connect to the database

    :param db_name: (str)
    The name of the database to connect to

    :param user_name: (str)
    The name of the user to authenticate as

    :param password: (str)
    The user's password

    :param schema_name: (str)
    The name of the schema where the table should be created

    :param table_name: (str)
    The name of the table to be created

    :param table_columns: (str)
    The columns definition of the table in the format "column_name DATA_TYPE, column_name DATA_TYPE, ..."
    '''
    # Connection to the PostgresSQL database
    conn = psycopg2.connect(
        host=endpoint_name,
        port=port,
        database=db_name,
        user=user_name,
        password=password,
    )

    # Creation of a cursor to execute SQL commands
    cur = conn.cursor()

    # Check if the table exists in the schema
    table_exists_query = f"SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_schema = '{schema_name}' AND table_name = '{table_name}')"
    cur.execute(table_exists_query)
    exists = cur.fetchone()[0]

    # If the table does not exist, create the table
    if not exists:
        create_table_query = f'CREATE TABLE {schema_name}.{table_name} ({table_columns})'
        cur.execute(create_table_query)

        unique_constraint_query = f'''
        ALTER TABLE {schema_name}.{table_name} ADD CONSTRAINT unique_id UNIQUE (id);'''
        cur.execute(unique_constraint_query)
        
        logging.info(
            f'The table {table_name} was created in the {schema_name} schema')
    else:
        logging.info(
            f'The table {table_name} already exists in the {schema_name} schema')

    # Commit changes and close the connection
    conn.commit()
    cur.close()
    conn.close()


def insert_data_into_postgresql(
        endpoint_name: str,
        port: str,
        datab_name: str,
        user_name: str,
        password: str,
        schema_name: str,
        table_name: str,
        df: pd.DataFrame,
        temp_schema_name: str) -> None:
    '''
    Function that inserts data from a Pandas DataFrame into a PostgreSQL table.
    If the table does not exist, it creates a new one in the specified schema.

    :param endpoint_name: (str)
    The endpoint URL of your Amazon RDS instance

    :param port: (int)
    The port number to connect to the database

    :param db_name: (str)
    The name of the database to connect to.

    :param user_name: (str)
    The name of the user to authenticate as.

    :param password: (str)
    The user's password.

    :param schema_name: (str)
    The name of the schema where the table should be created.

    :param table_name: (str)
    The name of the table to be created or where the data will be inserted.

    :param df: (pandas.DataFrame)
    The DataFrame containing the data to be inserted.
    '''

    # Connect to the PostgreSQL database
    db_host = endpoint_name
    db_port = port
    db_name = datab_name
    db_user = user_name
    db_pass = password

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_pass
    )
    # create engine
    engine = create_engine(
        f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')

    # Create a temporary table with the data from the DataFrame
    temp_table_name = f'temp_{table_name}'
    df.to_sql(
        name=temp_table_name,
        con=engine.connect(),
        schema=temp_schema_name,
        index=False,
        if_exists='replace')
    logging.info('Temporary table was created: SUCCESS')

    # Check if the final table exists
    inspector = inspect(engine)
    table_exists = inspector.has_table(table_name, schema=schema_name)

    if table_exists:
        # Check if the DataFrame columns match the table columns
        db_cols_query = f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND table_schema='{schema_name}'"
        with conn.cursor() as cur:
            cur.execute(db_cols_query)
            db_columns = [col[0] for col in cur.fetchall()]

        df_columns = df.columns.tolist()

        if db_columns != df_columns:
            raise ValueError(
                f'The columns of the DataFrame do not match the columns of the table {schema_name}.{table_name}')

        # Insert the data into the final table without overwriting existing data
        insert_query = f'INSERT INTO {schema_name}.{table_name} SELECT * FROM {temp_schema_name}.{temp_table_name} ON CONFLICT (id) DO NOTHING;'
        with conn.cursor() as cur:
            cur.execute(insert_query)
        logging.info('The dataframe data has been inserted: SUCCESS')

    # Remove the temporary table
    drop_query = f'DROP TABLE {temp_schema_name}.{temp_table_name};'

    with conn.cursor() as cur:
        cur.execute(drop_query)
    logging.info('The temp table has been removed: SUCCESS')

    # Close the database connection
    conn.commit()
    conn.close()
