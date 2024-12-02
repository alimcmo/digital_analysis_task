import pandas as pd
import os

def load_and_describe_data():
    # Get the directory containing the CSV files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    
    # Dictionary to store our dataframes
    dfs = {}
    
    # List of CSV files
    files = [
        'orders_master_table.csv',
        'orders_sku_master_table.csv',
        'orders_attribution_table.csv',
        'periods_weeks_reference.csv'
    ]
    
    # Load each CSV and print basic information
    for file in files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f"\n{'='*50}")
            print(f"Loading and analyzing {file}")
            print('='*50)
            
            # Load the CSV
            df = pd.read_csv(file_path)
            dfs[file] = df
            
            # Basic information about the dataset
            print("\nBasic Information:")
            print(f"Number of rows: {len(df)}")
            print(f"Number of columns: {len(df.columns)}")
            print("\nColumns:")
            print(df.columns.tolist())
            
            # Display data types of columns
            print("\nData Types:")
            print(df.dtypes)
            
            # Basic statistics for numeric columns
            print("\nNumeric Column Statistics:")
            print(df.describe())
            
            # Sample of first few rows
            print("\nFirst few rows:")
            print(df.head())
            
            # Check for missing values
            print("\nMissing Values:")
            print(df.isnull().sum())
    
    return dfs
if __name__ == "__main__":
    print("Loading and describing data...")
    dfs = load_and_describe_data()
