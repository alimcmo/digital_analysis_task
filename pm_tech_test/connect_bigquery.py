from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os

def setup_bigquery_connection():
    parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auth_directory = os.path.join(parent_directory, 'auth')

    # Path to your service account key JSON file
    KEY_PATH = os.path.join(auth_directory, 'recruitmentOAuthID.json')
    
    # Create credentials using the service account key
    credentials = service_account.Credentials.from_service_account_file(
        KEY_PATH,
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    
    # Create BigQuery client
    return bigquery.Client(
        credentials=credentials,
        project=credentials.project_id
    )

def fetch_data():
    client = setup_bigquery_connection()
    
    # Dictionary to store our dataframes
    dfs = {}
    
    # List of tables to query
    tables = [
        'orders_master_table',
        'orders_sku_master_table',
        'orders_attribution_table',
        'periods_weeks_reference'
    ]
    
    for table in tables:
        print(f"Fetching {table}...")
        query = f"""
        SELECT *
        FROM `recruitment-442513.junior_analyst_task.{table}`
        """
        
        try:
            # Convert query results directly to pandas DataFrame
            df = client.query(query).to_dataframe()
            dfs[table] = df
            print(f"Successfully fetched {table}: {len(df)} rows")
        except Exception as e:
            print(f"Error fetching {table}: {str(e)}")
    
    return dfs

if __name__ == "__main__":
    try:
        print("Connecting to BigQuery and fetching data...")
        dataframes = fetch_data()
        
        # Print basic info about each dataframe
        for name, df in dataframes.items():
            print(f"\n{name}:")
            print(f"Rows: {len(df)}")
            print(f"Columns: {df.columns.tolist()}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")