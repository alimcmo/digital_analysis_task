import pandas as pd
import os

def load_data():
    """Load all required datasets"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    
    # Load all datasets
    orders_master = pd.read_csv(os.path.join(data_dir, 'orders_master_table.csv'))
    orders_sku = pd.read_csv(os.path.join(data_dir, 'orders_sku_master_table.csv'))
    orders_attribution = pd.read_csv(os.path.join(data_dir, 'orders_attribution_table.csv'))
    periods_weeks = pd.read_csv(os.path.join(data_dir, 'periods_weeks_reference.csv'))
    
    return orders_master, orders_sku, orders_attribution, periods_weeks

def analyze_original_data(orders_master, orders_sku, orders_attribution):
    """Analyze the original datasets before merging"""
    print("\n=== Original Data Analysis ===")
    print(f"Orders Master Records: {len(orders_master)}")
    print(f"Original NET_REVENUE Sum: £{orders_master['NET_REVENUE'].sum():,.2f}")
    print(f"SKU Records: {len(orders_sku)}")
    print(f"Attribution Records: {len(orders_attribution)}")
    
    # Analyze NET_REVENUE
    print("\nNET_REVENUE Statistics:")
    print(orders_master['NET_REVENUE'].describe())
    
    # Check for any negative values
    print("\nNegative NET_REVENUE count:", len(orders_master[orders_master['NET_REVENUE'] < 0]))

def analyze_sku_data(orders_sku):
    """Analyze SKU-level data"""
    print("\n=== SKU Data Analysis ===")
    print("\nNET_ITEM_PRICE Statistics:")
    print(orders_sku['NET_ITEM_PRICE'].describe())
    
    print("\nQUANTITY Statistics:")
    print(orders_sku['QUANTITY'].describe())
    
    # Calculate theoretical revenue at SKU level
    sku_revenue = orders_sku['NET_ITEM_PRICE'] * orders_sku['QUANTITY']
    print(f"\nTheoretical SKU-based revenue: £{sku_revenue.sum():,.2f}")

def analyze_merged_data():
    """Analyze the merged dataset"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    merged_path = os.path.join(data_dir, 'merged_orders_data.csv')
    
    if os.path.exists(merged_path):
        merged_data = pd.read_csv(merged_path)
        print("\n=== Merged Data Analysis ===")
        print(f"Total records in merged data: {len(merged_data)}")
        print(f"TOTAL_REVENUE Sum: £{merged_data['TOTAL_REVENUE'].sum():,.2f}")
        print(f"NET_REVENUE Sum: £{merged_data['NET_REVENUE'].sum():,.2f}")
        
        # Analyze discrepancies
        print("\nRevenue Discrepancies:")
        revenue_diff = merged_data['NET_REVENUE'] - merged_data['TOTAL_REVENUE']
        print("Difference Statistics:")
        print(revenue_diff.describe())
        
        # Check for missing values
        print("\nMissing Values Analysis:")
        print(merged_data[['NET_REVENUE', 'TOTAL_REVENUE', 'NET_ITEM_PRICE', 'QUANTITY']].isnull().sum())
    else:
        print("\nMerged data file not found. Please run merge_data.py first.")

def analyze_data_relationships(orders_master, orders_sku):
    """Analyze relationships between master and SKU data"""
    print("\n=== Data Relationships Analysis ===")
    
    # Check for orders without SKUs
    master_orders = set(orders_master['NAME'])
    sku_orders = set(orders_sku['NAME'])
    
    missing_skus = master_orders - sku_orders
    print(f"Orders without SKU data: {len(missing_skus)}")
    
    if missing_skus:
        missing_revenue = orders_master[orders_master['NAME'].isin(missing_skus)]['NET_REVENUE'].sum()
        print(f"Revenue from orders without SKUs: £{missing_revenue:,.2f}")

def main():
    # Load all data
    orders_master, orders_sku, orders_attribution, periods_weeks = load_data()
    
    # Run all analyses
    analyze_original_data(orders_master, orders_sku, orders_attribution)
    analyze_sku_data(orders_sku)
    analyze_merged_data()
    analyze_data_relationships(orders_master, orders_sku)

if __name__ == "__main__":
    main()