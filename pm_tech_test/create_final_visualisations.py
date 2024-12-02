import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from scipy import stats
import scipy.stats as stats

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    
    orders_master = pd.read_csv(os.path.join(data_dir, 'orders_master_table.csv'))
    orders_sku = pd.read_csv(os.path.join(data_dir, 'orders_sku_master_table.csv'))
    orders_attribution = pd.read_csv(os.path.join(data_dir, 'orders_attribution_table.csv'))
    periods_weeks = pd.read_csv(os.path.join(data_dir, 'periods_weeks_reference.csv'))
    
    # Convert dates to datetime
    orders_master['CREATED_AT'] = pd.to_datetime(orders_master['CREATED_AT'])
    
    return orders_master, orders_sku, orders_attribution, periods_weeks

def merge_with_periods(df, periods_weeks):
    """Helper function to merge data with business periods"""
    df = df.copy()
    df['DATE'] = df['CREATED_AT'].dt.strftime('%Y-%m-%d')
    return df.merge(periods_weeks, on='DATE', how='left')

def create_sales_over_time(orders_master, periods_weeks):
    # Merge with periods and group by period
    df = merge_with_periods(orders_master, periods_weeks)
    sales_by_period = df.groupby('PERIOD').agg({
        'NET_REVENUE': 'sum',
        'NAME': 'count'
    }).reset_index()
    
    # Create subplot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Revenue over time
    sns.lineplot(data=sales_by_period, x='PERIOD', y='NET_REVENUE', ax=ax1, marker='o')
    ax1.set_title('Revenue by Business Period', pad=20)
    ax1.set_xlabel('Business Period')
    ax1.set_ylabel('Revenue (£)')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
    
    # Orders over time
    sns.lineplot(data=sales_by_period, x='PERIOD', y='NAME', ax=ax2, marker='o')
    ax2.set_title('Number of Orders by Business Period')
    ax2.set_xlabel('Business Period')
    ax2.set_ylabel('Number of Orders')
    
    plt.tight_layout()
    plt.savefig('sales_over_time.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_first_vs_repeat_orders(orders_master):
    plt.figure(figsize=(10, 6))
    order_types = orders_master['FIRST_OR_REPEAT'].value_counts()
    plt.pie(order_types, labels=order_types.index, autopct='%1.1f%%', startangle=90)
    plt.title('Distribution of First vs Repeat Orders', fontsize=16, pad=20)
    plt.axis('equal')
    plt.savefig('first_vs_repeat_orders.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_subscription_analysis(orders_master):
    plt.figure(figsize=(10, 6))
    sub_orders = orders_master['SUB_ORDER'].value_counts()
    ax = sns.barplot(x=sub_orders.index, y=sub_orders.values)
    plt.title('Subscription vs One-off Orders', fontsize=16, pad=20)
    plt.xlabel('Order Type', fontsize=12)
    plt.ylabel('Number of Orders', fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('subscription_vs_oneoff.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_order_value_barplot(orders_master):
    plt.figure(figsize=(10, 6))
    
    # Calculate statistics
    order_stats = orders_master.groupby('FIRST_OR_REPEAT').agg({
        'NET_REVENUE': ['mean', 'std']
    }).reset_index()
    order_stats.columns = ['FIRST_OR_REPEAT', 'mean', 'std']
    
    # Create bar plot
    ax = sns.barplot(
        data=order_stats, 
        x='FIRST_OR_REPEAT', 
        y='mean',
        color='lightcoral'
    )
    
    # Add error bars manually
    ax.errorbar(
        x=range(len(order_stats)),
        y=order_stats['mean'],
        yerr=order_stats['std'],
        fmt='none',
        color='black',
        capsize=5
    )
    
    # Customize appearance
    plt.title('Average Order Value by Customer Type', fontsize=14, pad=15)
    plt.xlabel('Customer Type', fontsize=12)
    plt.ylabel('Average Order Value (£)', fontsize=12)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{int(x):,}'))
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(order_stats['mean']):
        ax.text(i, v, f'£{v:,.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('order_value_barplot.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_discount_usage_analysis(orders_master):
    plt.figure(figsize=(10, 6))
    discount_usage = orders_master['DISCOUNT_CODE'].ne('(not set)').value_counts()
    plt.pie(discount_usage, 
            labels=['No Discount', 'With Discount'],
            autopct='%1.1f%%',
            startangle=90)
    plt.title('Orders With vs Without Discount', fontsize=16, pad=20)
    plt.axis('equal')
    plt.savefig('discount_usage.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_top_products_chart(orders_sku):
    product_revenue = orders_sku.groupby('ITEM_NAME').agg({
        'NET_ITEM_PRICE': lambda x: (x * orders_sku.loc[x.index, 'QUANTITY']).sum()
    }).reset_index()
    
    top_10_products = product_revenue.nlargest(10, 'NET_ITEM_PRICE')
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=top_10_products, 
        x='ITEM_NAME', 
        y='NET_ITEM_PRICE',
        hue='ITEM_NAME',
        legend=False
    )
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
    
    plt.title('Top 10 Products by Revenue', fontsize=16, pad=20)
    plt.xlabel('Product Name', fontsize=12)
    plt.ylabel('Total Revenue (£)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('top_products.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_marketing_channel_chart(orders_attribution, orders_master):
    channel_data = pd.merge(
        orders_attribution,
        orders_master[['NAME', 'NET_REVENUE']],
        left_on='order_name',
        right_on='NAME',
        how='left'
    )
    
    channel_revenue = channel_data.groupby('default_channel_group')['NET_REVENUE'].sum().reset_index()
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=channel_revenue,
        x='default_channel_group',
        y='NET_REVENUE',
        hue='default_channel_group',
        legend=False
    )
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
    
    plt.title('Revenue by Marketing Channel', fontsize=16, pad=20)
    plt.xlabel('Marketing Channel', fontsize=12)
    plt.ylabel('Total Revenue (£)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('channel_revenue.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_discount_codes_pie(orders_master):
    # Replace '(not set)' with 'No Discount' before grouping
    orders_master = orders_master.copy()
    orders_master['DISCOUNT_CODE'] = orders_master['DISCOUNT_CODE'].replace('(not set)', 'No Discount')
    
    discount_revenue = orders_master.groupby('DISCOUNT_CODE')['NET_REVENUE'].sum()
    top_10_discounts = discount_revenue.nlargest(10)
    
    plt.figure(figsize=(12, 8))
    plt.pie(top_10_discounts, 
            labels=top_10_discounts.index,
            autopct='%1.1f%%',
            pctdistance=0.85,
            startangle=90)
    
    plt.title('Top 10 Discount Codes by Revenue Share', fontsize=16, pad=20)
    plt.axis('equal')
    plt.savefig('top_discount_codes_pie.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_basket_size_analysis(orders_sku):
    """Analyze basket sizes"""
    basket_sizes = orders_sku.groupby('NAME')['QUANTITY'].sum().reset_index()
    
    plt.figure(figsize=(12, 8))
    sns.histplot(data=basket_sizes, x='QUANTITY', bins=30, color='lightcoral', stat='count', alpha=0.8)
    plt.title('Distribution of Order Sizes', fontsize=14, pad=15)
    plt.xlabel('Items per Order', fontsize=12)
    plt.ylabel('Number of Orders (log scale)', fontsize=12)
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('basket_size_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_monthly_retention_analysis(orders_master, periods_weeks):
    df = merge_with_periods(orders_master, periods_weeks)
    
    # Get first purchase period for each customer
    first_purchases = df.groupby('CUSTOMER_ID')['PERIOD'].min().reset_index()
    first_purchases.columns = ['CUSTOMER_ID', 'FIRST_PERIOD']
    
    # Merge back to get retention by period
    df = df.merge(first_purchases, on='CUSTOMER_ID')
    df['PERIODS_SINCE_FIRST'] = df['PERIOD'] - df['FIRST_PERIOD']
    
    retention_data = df.groupby(['FIRST_PERIOD', 'PERIODS_SINCE_FIRST'])['CUSTOMER_ID'].nunique().reset_index()
    
    # Fix pivot syntax
    pivot_table = retention_data.pivot(
        index='FIRST_PERIOD',
        columns='PERIODS_SINCE_FIRST',
        values='CUSTOMER_ID'
    )
    
    plt.figure(figsize=(15, 8))
    sns.heatmap(pivot_table, cmap='YlOrRd', annot=True, fmt='g')
    
    plt.title('Customer Retention by Business Period', pad=20)
    plt.xlabel('Periods Since First Purchase')
    plt.ylabel('First Purchase Period')
    
    plt.tight_layout()
    plt.savefig('retention_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_purchase_frequency_analysis(orders_master):
    """Analyze customer purchase frequency"""
    df = orders_master.copy()
    
    # Calculate days between orders for each customer
    customer_orders = df.groupby('CUSTOMER_ID')['CREATED_AT'].agg(list).reset_index()
    
    # Calculate average days between orders
    def get_avg_days_between_orders(dates):
        if len(dates) < 2:
            return None
        dates = sorted(dates)
        differences = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        return np.mean(differences)
    
    customer_orders['avg_days_between_orders'] = customer_orders['CREATED_AT'].apply(get_avg_days_between_orders)
    
    # Plot distribution of purchase frequency
    plt.figure(figsize=(10, 6))
    sns.histplot(data=customer_orders.dropna(), x='avg_days_between_orders', bins=50)
    plt.title('Distribution of Days Between Customer Purchases', fontsize=16, pad=20)
    plt.xlabel('Average Days Between Orders', fontsize=12)
    plt.ylabel('Number of Customers', fontsize=12)
    plt.savefig('purchase_frequency.png', dpi=300, bbox_inches='tight')
    plt.close()

def analyze_statistical_significance(orders_master):
    """Perform statistical analysis"""
    # Compare first vs repeat order values
    first_orders = orders_master[orders_master['FIRST_OR_REPEAT'] == 'FIRST']['NET_REVENUE']
    repeat_orders = orders_master[orders_master['FIRST_OR_REPEAT'] == 'REPEAT']['NET_REVENUE']
    
    t_stat, p_value = stats.ttest_ind(first_orders, repeat_orders)
    
    with open('statistical_analysis.txt', 'w') as f:
        f.write("Statistical Analysis Results\n")
        f.write("===========================\n\n")
        f.write(f"T-statistic: {t_stat:.4f}\n")
        f.write(f"P-value: {p_value:.4f}\n")
        f.write(f"\nFirst Orders Mean: £{first_orders.mean():.2f}\n")
        f.write(f"Repeat Orders Mean: £{repeat_orders.mean():.2f}\n")
        f.write(f"\nFirst Orders Std: £{first_orders.std():.2f}\n")
        f.write(f"Repeat Orders Std: £{repeat_orders.std():.2f}\n")

def create_subscription_order_value_comparison(orders_master):
    """Compare average order values between subscription and non-subscription orders"""
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=orders_master, x='SUB_ORDER', y='NET_REVENUE')
    plt.title('Order Value Distribution: Subscription vs Non-Subscription', fontsize=16, pad=20)
    plt.xlabel('Order Type', fontsize=12)
    plt.ylabel('Order Value (£)', fontsize=12)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('subscription_order_values.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_marketing_channel_by_customer_type(orders_attribution, orders_master):
    """Analyze marketing channels effectiveness for first-time vs repeat customers"""
    # Check data before merge
    print("Orders Attribution shape:", orders_attribution.shape)
    print("Orders Master shape:", orders_master.shape)
    print("\nSample of orders_attribution default_channel_group:")
    print(orders_attribution['default_channel_group'].value_counts())
    
    # Merge attribution and order data
    merged_data = pd.merge(
        orders_attribution,
        orders_master[['NAME', 'NET_REVENUE', 'FIRST_OR_REPEAT']],
        left_on='order_name',
        right_on='NAME',
        how='left'
    )
    
    # Check data after merge
    print("\nMerged data shape:", merged_data.shape)
    print("\nDefault channel groups after merge:")
    print(merged_data['default_channel_group'].value_counts(dropna=False))
    
    # Calculate average revenue by channel and customer type
    channel_performance = merged_data.groupby(
        ['default_channel_group', 'FIRST_OR_REPEAT']
    )['NET_REVENUE'].mean().reset_index()
    
    plt.figure(figsize=(15, 8))
    sns.barplot(
        data=channel_performance,
        x='default_channel_group',
        y='NET_REVENUE',
        hue='FIRST_OR_REPEAT'
    )
    
    plt.title('Average Order Value by Marketing Channel and Customer Type', fontsize=16, pad=20)
    plt.xlabel('Marketing Channel', fontsize=12)
    plt.ylabel('Average Order Value (£)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
    plt.grid(True, alpha=0.3)
    plt.legend(title='Customer Type')
    plt.tight_layout()
    plt.savefig('marketing_channel_by_customer_type.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_free_gifts_analysis(orders_master, orders_sku):
    """Analyze the impact of free gifts on order value with improved visualization"""
    # Merge orders_master with orders_sku to get item information
    merged_data = pd.merge(
        orders_master,
        orders_sku[['NAME', 'ITEM_NAME', 'FREE_GIFT_FLAG']],
        on='NAME',
        how='left'
    )
    
    # Identify orders with free gifts using multiple criteria
    merged_data['HAS_FREE_GIFT'] = (
        (merged_data['DISCOUNT_CODE'].str.contains('FREE', case=False, na=False)) |
        (merged_data['ITEM_NAME'].str.contains('Gift', case=False, na=False)) |
        (merged_data['FREE_GIFT_FLAG'] == 1)
    )
    
    # Create figure with two complementary visualizations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. Bar plot showing average order values
    avg_order_values = merged_data.groupby(['HAS_FREE_GIFT', 'FIRST_OR_REPEAT'])['NET_REVENUE'].mean().reset_index()
    sns.barplot(
        data=avg_order_values,
        x='HAS_FREE_GIFT',
        y='NET_REVENUE',
        hue='FIRST_OR_REPEAT',
        ax=ax1
    )
    ax1.set_title('Average Order Value')
    ax1.set_xlabel('Has Free Gift')
    ax1.set_ylabel('Average Order Value (£)')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
    
    # 2. Count plot showing number of orders
    order_counts = merged_data.drop_duplicates('NAME').copy()  # Count unique orders only
    sns.countplot(
        data=order_counts,
        x='HAS_FREE_GIFT',
        hue='FIRST_OR_REPEAT',
        ax=ax2
    )
    ax2.set_title('Number of Orders')
    ax2.set_xlabel('Has Free Gift')
    ax2.set_ylabel('Number of Orders')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    # Overall title and formatting
    plt.suptitle('Free Gifts Analysis: Impact on Order Values and Frequency', fontsize=16, y=1.05)
    plt.tight_layout()
    
    # Add value labels on bars
    for ax in [ax1, ax2]:
        for container in ax.containers:
            ax.bar_label(container, fmt='£%.0f' if ax == ax1 else '%.0f')
    
    plt.savefig('free_gifts_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_product_popularity_by_customer_type(orders_sku, orders_master):
    """Analyze product popularity between first-time and repeat customers"""
    # Merge SKU data with order data to get customer type
    merged_data = pd.merge(
        orders_sku,
        orders_master[['NAME', 'FIRST_OR_REPEAT']],
        on='NAME',
        how='left'
    )
    
    # Calculate total quantity sold by product and customer type
    product_popularity = merged_data.groupby(
        ['ITEM_NAME', 'FIRST_OR_REPEAT']
    )['QUANTITY'].sum().reset_index()
    
    # Get top 10 products overall
    top_products = product_popularity.groupby('ITEM_NAME')['QUANTITY'].sum().nlargest(10).index
    
    # Filter for top products
    plot_data = product_popularity[product_popularity['ITEM_NAME'].isin(top_products)]
    
    plt.figure(figsize=(15, 8))
    sns.barplot(
        data=plot_data,
        x='ITEM_NAME',
        y='QUANTITY',
        hue='FIRST_OR_REPEAT'
    )
    
    plt.title('Top 10 Products: Popularity Among First-time vs Repeat Customers', fontsize=16, pad=20)
    plt.xlabel('Product Name', fontsize=12)
    plt.ylabel('Total Quantity Sold', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.legend(title='Customer Type')
    plt.tight_layout()
    plt.savefig('product_popularity_by_customer_type.png', dpi=300, bbox_inches='tight')
    plt.close()

def calculate_total_revenue(orders_master):
    total_revenue = orders_master['NET_REVENUE'].sum()
    print(f"\nTotal Revenue: £{total_revenue:,.2f}")
    
    # Also show revenue by year for context
    yearly_revenue = orders_master.groupby(orders_master['CREATED_AT'].dt.year)['NET_REVENUE'].sum()
    print("\nRevenue by Year:")
    for year, revenue in yearly_revenue.items():
        print(f"{year}: £{revenue:,.2f}")
    
    return total_revenue

def clean_data(orders_master, orders_sku, orders_attribution):
    """Clean and validate data before visualization"""
    
    # 1. Remove duplicates
    orders_master = orders_master.drop_duplicates('NAME')
    orders_sku = orders_sku.drop_duplicates(['NAME', 'ITEM_SKU'])
    orders_attribution = orders_attribution.drop_duplicates('order_name')
    
    # 2. Standardize gift identification in SKU data
    orders_sku = orders_sku.copy()
    orders_sku['is_gift'] = (
        (orders_sku['FREE_GIFT_FLAG'] == 1) |
        (orders_sku['ITEM_NAME'].str.contains('Gift', case=False, na=False))
    )
    
    # 3. Remove outliers for visualization purposes
    def remove_outliers(df, column):
        q1 = df[column].quantile(0.01)
        q3 = df[column].quantile(0.99)
        iqr = q3 - q1
        return df[
            (df[column] >= q1 - 1.5 * iqr) &
            (df[column] <= q3 + 1.5 * iqr)
        ]
    
    orders_master = remove_outliers(orders_master, 'NET_REVENUE')
    
    print("\n=== Data Cleaning Summary ===")
    print(f"Orders remaining after cleaning: {len(orders_master)}")
    print(f"SKUs remaining after cleaning: {len(orders_sku)}")
    print(f"Attribution records remaining: {len(orders_attribution)}")
    
    return orders_master, orders_sku, orders_attribution

def visualize_auto_renew_impact(orders_master, orders_sku):
    """Create a clear table visualization of 25% auto-renew deal impact"""
    
    # Identify orders with 25% auto-renew deals
    auto_renew_25_off = orders_sku[
        orders_sku['ITEM_SKU'].str.contains('25.00% Off Auto renew', case=False, na=False) |
        orders_sku['ITEM_NAME'].str.contains('25.00% Off Auto renew', case=False, na=False)
    ]['NAME'].unique()
    
    # Get customer purchase history
    df = orders_master.copy()
    
    # Calculate metrics for customers with auto-renew
    customer_metrics = []
    
    for customer_id in df['CUSTOMER_ID'].unique():
        customer_orders = df[df['CUSTOMER_ID'] == customer_id].sort_values('CREATED_AT')
        
        if customer_orders['NAME'].isin(auto_renew_25_off).any():
            first_auto_renew = customer_orders[customer_orders['NAME'].isin(auto_renew_25_off)]['CREATED_AT'].min()
            
            before_dates = customer_orders[customer_orders['CREATED_AT'] < first_auto_renew]['CREATED_AT'].tolist()
            after_dates = customer_orders[customer_orders['CREATED_AT'] >= first_auto_renew]['CREATED_AT'].tolist()
            
            if len(before_dates) >= 2 and len(after_dates) >= 2:
                def calc_avg_days(dates):
                    dates = sorted(dates)
                    return np.mean([(dates[i+1] - dates[i]).days for i in range(len(dates)-1)])
                
                customer_metrics.append({
                    'customer_id': customer_id,
                    'avg_days_before': calc_avg_days(before_dates),
                    'avg_days_after': calc_avg_days(after_dates)
                })
    
    metrics_df = pd.DataFrame(customer_metrics)
    
    # Calculate statistics
    mean_before = metrics_df['avg_days_before'].mean()
    mean_after = metrics_df['avg_days_after'].mean()
    t_stat, p_value = stats.ttest_rel(metrics_df['avg_days_before'], metrics_df['avg_days_after'])
    
    # Create figure for table
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Define table data
    table_data = [
        ['Metric', 'Value'],
        ['Total Customers with Auto-Renew', f'{len(metrics_df):,}'],
        ['Average Days Between Orders (Before)', f'{mean_before:.1f}'],
        ['Average Days Between Orders (After)', f'{mean_after:.1f}'],
        ['Reduction in Days Between Orders', f'{mean_before - mean_after:+.1f}'],
        ['Percentage Improvement', f'{((mean_before - mean_after) / mean_before * 100):.1f}%'],
        ['Statistical Significance (p-value)', f'{p_value:.4f}'],
        ['t-statistic', f'{t_stat:.2f}']
    ]
    
    # Create table
    table = ax.table(cellText=table_data,
                    cellLoc='left',
                    loc='center',
                    colWidths=[0.6, 0.4])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.8)
    
    # Style header row
    for i in range(2):
        table[(0, i)].set_facecolor('#E6E6E6')
        table[(0, i)].set_text_props(weight='bold')
    
    # Add title
    plt.title('Impact of 25% Auto-Renew Deal on Purchase Frequency', 
              pad=20, fontsize=14, fontweight='bold')
    
    plt.savefig('auto_renew_impact_table.png', 
                dpi=300, bbox_inches='tight',
                facecolor='white')
    plt.close()
    
    return metrics_df

def create_clv_by_period(orders_master, periods_weeks):
    """Create visualization of average Customer Lifetime Value by business period"""
    # Merge with periods reference
    df = merge_with_periods(orders_master, periods_weeks)
    
    # Calculate average CLV by period
    clv_by_period = df.groupby(['PERIOD', 'CUSTOMER_ID'])['NET_REVENUE'].sum().reset_index()
    avg_clv_by_period = clv_by_period.groupby('PERIOD')['NET_REVENUE'].mean().reset_index()
    
    # Create visualization
    plt.figure(figsize=(15, 6))
    sns.lineplot(
        data=avg_clv_by_period,
        x='PERIOD',
        y='NET_REVENUE',
        marker='o',
        color='lightcoral'
    )
    
    plt.title('Average Customer Lifetime Value by Business Period', fontsize=16, pad=20)
    plt.xlabel('Business Period', fontsize=12)
    plt.ylabel('Average CLV (£)', fontsize=12)
    
    # Format y-axis to show pounds
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:.2f}'))
    
    # Add grid for easier reading
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig('customer_lifetime_value.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Load data
    orders_master, orders_sku, orders_attribution, periods_weeks = load_data()
    
    # Clean data
    orders_master, orders_sku, orders_attribution = clean_data(
        orders_master, orders_sku, orders_attribution
    )
    
    # Calculate total revenue
    calculate_total_revenue(orders_master)
    
    # Create original visualizations
    create_top_products_chart(orders_sku)
    create_marketing_channel_chart(orders_attribution, orders_master)
    create_discount_codes_pie(orders_master)
    
    # Create additional visualizations
    create_sales_over_time(orders_master, periods_weeks)
    create_first_vs_repeat_orders(orders_master)
    create_subscription_analysis(orders_master)
    create_order_value_barplot(orders_master)
    create_discount_usage_analysis(orders_master)
    create_basket_size_analysis(orders_sku)
    create_monthly_retention_analysis(orders_master, periods_weeks)
    create_purchase_frequency_analysis(orders_master)
    analyze_statistical_significance(orders_master)
    create_subscription_order_value_comparison(orders_master)
    create_marketing_channel_by_customer_type(orders_attribution, orders_master)
    create_free_gifts_analysis(orders_master, orders_sku)
    create_product_popularity_by_customer_type(orders_sku, orders_master)
    visualize_auto_renew_impact(orders_master, orders_sku)
    create_clv_by_period(orders_master, periods_weeks)
    
    print("All visualizations have been created successfully!")

if __name__ == "__main__":
    main()