import pandas as pd
import os

def load_data():
    """Load the orders master table"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    
    orders_master = pd.read_csv(os.path.join(data_dir, 'orders_master_table.csv'))
    # Convert dates to datetime
    orders_master['CREATED_AT'] = pd.to_datetime(orders_master['CREATED_AT'])
    
    return orders_master

def validate_first_orders(orders_master):
    """Validate if FIRST orders are correctly classified"""
    
    # Group by customer and check their orders
    customer_analysis = orders_master.groupby('CUSTOMER_ID').agg({
        'NAME': 'count',  # Total number of orders
        'FIRST_OR_REPEAT': lambda x: sum(x == 'FIRST'),  # Count of FIRST orders
        'CREATED_AT': 'min'  # First order date
    }).reset_index()
    
    # Find problematic cases
    problems = customer_analysis[customer_analysis['FIRST_OR_REPEAT'] > 1]
    
    print("\nValidation Results:")
    print(f"Total customers: {len(customer_analysis)}")
    print(f"Customers with multiple FIRST orders: {len(problems)}")
    
    if len(problems) > 0:
        print("\nExample of problematic customers:")
        for _, row in problems.head().iterrows():
            print(f"\nCustomer ID: {row['CUSTOMER_ID']}")
            customer_orders = orders_master[orders_master['CUSTOMER_ID'] == row['CUSTOMER_ID']]
            print(customer_orders[['NAME', 'CREATED_AT', 'FIRST_OR_REPEAT', 'NET_REVENUE']]
                  .sort_values('CREATED_AT'))
    
    return problems

def analyze_customer_ordering_patterns(orders_master):
    """Analyze patterns in customer ordering behavior"""
    
    # Get first order date for each customer
    first_orders = orders_master.groupby('CUSTOMER_ID')['CREATED_AT'].min().reset_index()

def main():
    print("Starting analysis...")
    
    # Load data
    orders_master = load_data()
    print(f"\nLoaded {len(orders_master)} orders")
    
    # Validate first orders
    print("\n=== Validating First Orders ===")
    problems = validate_first_orders(orders_master)
    
    # Analyze ordering patterns
    print("\n=== Analyzing Order Patterns ===")
    order_sequence = analyze_customer_ordering_patterns(orders_master)
    
    # Additional summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total orders: {len(orders_master):,}")
    print(f"Total customers: {orders_master['CUSTOMER_ID'].nunique():,}")
    print(f"Average orders per customer: {len(orders_master) / orders_master['CUSTOMER_ID'].nunique():.2f}")
    
    # Print FIRST vs REPEAT distribution
    print("\n=== Order Type Distribution ===")
    print(orders_master['FIRST_OR_REPEAT'].value_counts(normalize=True).mul(100).round(1).astype(str) + '%')
    
    return problems, order_sequence

if __name__ == "__main__":
    problems, order_sequence = main()
