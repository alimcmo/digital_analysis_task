import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_basic_visualizations(orders_df, periods_df):
    """
    Create some basic visualizations for sales analysis
    """
    # 1. Sales Over Time
    plt.figure(figsize=(15, 6))
    
    # Convert CREATED_AT to datetime and format for grouping
    orders_df['CREATED_AT'] = pd.to_datetime(orders_df['CREATED_AT'])
    orders_df['month'] = orders_df['CREATED_AT'].dt.strftime('%Y-%m')
    
    # Create the visualization
    orders_by_period = orders_df.groupby('month')['NET_REVENUE'].sum().reset_index()
    sns.lineplot(data=orders_by_period, x='month', y='NET_REVENUE')
    plt.title('Total Sales by Month')
    plt.xticks(rotation=45)
    # Format y-axis with pound signs
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
    plt.tight_layout()
    plt.savefig('sales_by_period.png')
    plt.close()

    # 2. First vs Repeat Orders
    plt.figure(figsize=(10, 6))
    order_types = orders_df['FIRST_OR_REPEAT'].value_counts()
    order_types.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Distribution of First vs Repeat Orders')
    plt.savefig('first_vs_repeat_orders.png')
    plt.close()

    # 3. Subscription vs One-off Orders
    plt.figure(figsize=(10, 6))
    sub_orders = orders_df['SUB_ORDER'].value_counts()
    sns.barplot(x=sub_orders.index, y=sub_orders.values)
    plt.title('Subscription vs One-off Orders')
    plt.savefig('subscription_vs_oneoff.png')
    plt.close()

    # 4. Average Order Value by Customer Type
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=orders_df, x='FIRST_OR_REPEAT', y='NET_REVENUE')
    plt.title('Order Value Distribution by Customer Type')
    plt.savefig('order_value_by_customer_type.png')
    plt.close()

    # 5. Discount Code Usage
    discount_usage = orders_df['DISCOUNT_CODE'].ne('(not set)').value_counts()
    plt.figure(figsize=(10, 6))
    discount_usage.plot(kind='pie', autopct='%1.1f%%', labels=['No Discount', 'With Discount'])
    plt.title('Orders With vs Without Discount')
    plt.savefig('discount_usage.png')
    plt.close()

def main():
    
    # Get the directory containing the CSV files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    
    # Load the data with proper paths
    orders_df = pd.read_csv(os.path.join(data_dir, 'orders_master_table.csv'))
    periods_df = pd.read_csv(os.path.join(data_dir, 'periods_weeks_reference.csv'))

    # Clean up the data if needed
    if 'date' in orders_df.columns:
        orders_df['date'] = pd.to_datetime(orders_df['date'])

    # Create visualizations
    create_basic_visualizations(orders_df, periods_df)

if __name__ == "__main__":
    main()