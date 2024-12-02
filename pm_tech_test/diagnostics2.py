import pandas as pd
import os

def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    
    orders_master = pd.read_csv(os.path.join(data_dir, 'orders_master_table.csv'))
    orders_sku = pd.read_csv(os.path.join(data_dir, 'orders_sku_master_table.csv'))
    orders_attribution = pd.read_csv(os.path.join(data_dir, 'orders_attribution_table.csv'))
    periods_weeks = pd.read_csv(os.path.join(data_dir, 'periods_weeks_reference.csv'))
    
    # Convert dates to datetime
    orders_master['CREATED_AT'] = pd.to_datetime(orders_master['CREATED_AT'], errors='coerce')
    
    return orders_master, orders_sku, orders_attribution, periods_weeks

def check_data_quality(orders_master, orders_sku, orders_attribution, periods_weeks):
    print("\n=== Data Quality Checks ===")
    
    # Check for missing values
    print("\nMissing Values:")
    print("Orders Master:")
    print(orders_master.isnull().sum())
    print("\nOrders SKU:")
    print(orders_sku.isnull().sum())
    print("\nOrders Attribution:")
    print(orders_attribution.isnull().sum())
    print("\nPeriods Weeks:")
    print(periods_weeks.isnull().sum())
    
    # Check for duplicates
    print("\nDuplicate Rows:")
    print(f"Orders Master: {orders_master.duplicated().sum()}")
    print(f"Orders SKU: {orders_sku.duplicated().sum()}")
    print(f"Orders Attribution: {orders_attribution.duplicated().sum()}")
    
    # Check for invalid numeric values
    print("\nInvalid Numeric Values:")
    print(f"Negative NET_REVENUE in Orders Master: {(orders_master['NET_REVENUE'] < 0).sum()}")
    print(f"Negative NET_ITEM_PRICE in Orders SKU: {(orders_sku['NET_ITEM_PRICE'] < 0).sum()}")
    print(f"Invalid QUANTITY in Orders SKU: {(orders_sku['QUANTITY'] <= 0).sum()}")
    
    # Check for date range issues
    print("\nDate Range Issues:")
    print(f"Earliest order date: {orders_master['CREATED_AT'].min()}")
    print(f"Latest order date: {orders_master['CREATED_AT'].max()}")
    
    # Check for consistency across tables
    print("\nCross-table Consistency:")
    master_orders = set(orders_master['NAME'])
    sku_orders = set(orders_sku['NAME'])
    attribution_orders = set(orders_attribution['order_name'])
    
    print(f"Orders in Master but not in SKU: {len(master_orders - sku_orders)}")
    print(f"Orders in Master but not in Attribution: {len(master_orders - attribution_orders)}")
    print(f"Orders in SKU but not in Master: {len(sku_orders - master_orders)}")
    print(f"Orders in Attribution but not in Master: {len(attribution_orders - master_orders)}")
    
    # Check for unusual patterns in categorical data
    print("\nCategorical Data Patterns:")
    print("Orders Master 'DISCOUNT_CODE' unique values:")
    print(orders_master['DISCOUNT_CODE'].value_counts())
    print("\nOrders Attribution 'default_channel_group' unique values:")
    print(orders_attribution['default_channel_group'].value_counts())

def check_price_anomalies(orders_sku):
    """Analyze price anomalies in the SKU table"""
    print("\n=== Price Anomaly Analysis ===")
    
    # Check for zero and negative prices
    zero_price = orders_sku[orders_sku['NET_ITEM_PRICE'] == 0]
    negative_price = orders_sku[orders_sku['NET_ITEM_PRICE'] < 0]
    
    print(f"\nZero price items: {len(zero_price)}")
    print(f"Negative price items: {len(negative_price)}")
    
    # Analyze zero price items
    zero_price_no_gift = zero_price[zero_price['FREE_GIFT_FLAG'] == 0]
    print(f"\nZero price items without free gift flag: {len(zero_price_no_gift)}")
    
    if len(zero_price_no_gift) > 0:
        print("\nSample of zero price items without free gift flag:")
        sample_cols = ['NAME', 'ITEM_SKU', 'ITEM_NAME', 'QUANTITY', 'NET_ITEM_PRICE', 'FREE_GIFT_FLAG']
        print(zero_price_no_gift[sample_cols].head())
        
        # Group by SKU to see patterns
        print("\nMost common SKUs with zero price and no free gift flag:")
        print(zero_price_no_gift['ITEM_SKU'].value_counts().head())
        
        # Group by item name to see patterns
        print("\nMost common item names with zero price and no free gift flag:")
        print(zero_price_no_gift['ITEM_NAME'].value_counts().head())
    
    return zero_price_no_gift

def analyze_zero_price_items(orders_sku, orders_master):
    """Detailed analysis of zero-price items"""
    print("\n=== Zero Price Items Analysis ===")
    
    # Get zero price items
    zero_price = orders_sku[orders_sku['NET_ITEM_PRICE'] == 0].copy()
    
    # 1. Basic Statistics
    print(f"\n1. Basic Statistics:")
    print(f"Total SKU rows: {len(orders_sku)}")
    print(f"Zero price items: {len(zero_price)} ({len(zero_price)/len(orders_sku)*100:.1f}%)")
    print(f"With free gift flag: {len(zero_price[zero_price['FREE_GIFT_FLAG'] == 1])}")
    print(f"Without free gift flag: {len(zero_price[zero_price['FREE_GIFT_FLAG'] == 0])}")
    
    # 2. Analyze items with "Gift" in name but no free gift flag
    gift_in_name = zero_price[
        (zero_price['FREE_GIFT_FLAG'] == 0) & 
        (zero_price['ITEM_NAME'].str.contains('Gift', case=False, na=False))
    ]
    print(f"\n2. Items with 'Gift' in name but no free gift flag: {len(gift_in_name)}")
    
    # 3. Check if these orders used discount codes
    merged_data = pd.merge(
        zero_price[zero_price['FREE_GIFT_FLAG'] == 0],
        orders_master[['NAME', 'DISCOUNT_CODE']],
        on='NAME',
        how='left'
    )
    
    print("\n3. Discount Code Analysis for Zero-Price Items:")
    print(merged_data['DISCOUNT_CODE'].value_counts().head())
    
    # 4. Pattern Analysis
    print("\n4. Pattern Analysis:")
    print("\nTop SKUs with zero price (excluding items with 'Gift' in name):")
    non_gift_zero = zero_price[
        ~zero_price['ITEM_NAME'].str.contains('Gift', case=False, na=False)
    ]
    print(non_gift_zero['ITEM_SKU'].value_counts().head())
    
    # 5. Check order totals for these items
    zero_price_orders = set(zero_price['NAME'])
    order_totals = orders_master[orders_master['NAME'].isin(zero_price_orders)]
    
    print("\n5. Order Total Analysis:")
    print(f"Average order value for orders with zero-price items: £{order_totals['NET_REVENUE'].mean():.2f}")
    print(f"Median order value for orders with zero-price items: £{order_totals['NET_REVENUE'].median():.2f}")
    
    return zero_price, gift_in_name, merged_data

def analyze_gift_inconsistencies(orders_sku):
    """Analyze inconsistencies in gift flagging"""
    # Items with 'Gift' in name
    gift_in_name = orders_sku['ITEM_NAME'].str.contains('Gift', case=False, na=False)
    gift_flag = orders_sku['FREE_GIFT_FLAG'] == 1
    zero_price = orders_sku['NET_ITEM_PRICE'] == 0
    
    print("\n=== Gift Flag Analysis ===")
    print(f"Total items with 'Gift' in name: {gift_in_name.sum()}")
    print(f"Total items with gift flag: {gift_flag.sum()}")
    print(f"Items with 'Gift' in name but no flag: {(gift_in_name & ~gift_flag).sum()}")
    print(f"Items with flag but no 'Gift' in name: {(~gift_in_name & gift_flag).sum()}")
    
    # Analyze zero-price gifts
    print("\nZero Price Gift Analysis:")
    print(f"Zero-price items with 'Gift' in name: {(gift_in_name & zero_price).sum()}")
    print(f"Zero-price items with gift flag: {(gift_flag & zero_price).sum()}")
    
    return orders_sku[gift_in_name & ~gift_flag]  # Return inconsistent items

def analyze_zero_price_patterns(orders_sku, orders_master):
    """Analyze patterns in zero-price items"""
    zero_price_items = orders_sku[orders_sku['NET_ITEM_PRICE'] == 0].copy()
    
    # Merge with orders_master to get discount information
    merged_data = pd.merge(
        zero_price_items,
        orders_master[['NAME', 'DISCOUNT_CODE', 'NET_REVENUE']],
        on='NAME',
        how='left'
    )
    
    print("\n=== Zero Price Patterns ===")
    
    # Categorize zero-price items
    merged_data['category'] = 'Unknown'
    merged_data.loc[merged_data['FREE_GIFT_FLAG'] == 1, 'category'] = 'Flagged Gift'
    merged_data.loc[merged_data['ITEM_NAME'].str.contains('Gift', case=False, na=False), 'category'] = 'Gift in Name'
    merged_data.loc[merged_data['DISCOUNT_CODE'] != '(not set)', 'category'] = 'Has Discount Code'
    
    print("\nZero Price Categories:")
    print(merged_data['category'].value_counts())
    
    # Analyze order values
    print("\nOrder Value Analysis by Category:")
    print(merged_data.groupby('category')['NET_REVENUE'].agg(['mean', 'median', 'count']))
    
    return merged_data

def analyze_problematic_skus(orders_sku):
    """Analyze SKUs with pricing inconsistencies"""
    # Group by SKU and analyze pricing patterns
    sku_analysis = orders_sku.groupby('ITEM_SKU').agg({
        'NET_ITEM_PRICE': ['nunique', 'min', 'max', 'mean'],
        'FREE_GIFT_FLAG': 'sum',
        'NAME': 'count'
    }).reset_index()
    
    # Find SKUs that sometimes have zero price and sometimes don't
    inconsistent_pricing = sku_analysis[
        (sku_analysis[('NET_ITEM_PRICE', 'min')] == 0) & 
        (sku_analysis[('NET_ITEM_PRICE', 'max')] > 0)
    ]
    
    print("\n=== SKU Pricing Analysis ===")
    print(f"\nSKUs with inconsistent pricing (sometimes zero, sometimes not): {len(inconsistent_pricing)}")
    
    if len(inconsistent_pricing) > 0:
        print("\nTop 5 SKUs with inconsistent pricing:")
        print(inconsistent_pricing.head())
    
    return inconsistent_pricing

def standardize_marketing_channels(orders_attribution):
    """Standardize marketing channel names"""
    # Create mapping for similar channel names
    channel_mapping = {
        '(not set)': 'Unknown',
        'Paid Shopping - Brand': 'Paid Shopping',
        'Paid - Generic': 'Paid Shopping',
        'Paid Search Brand': 'Paid Shopping',
        'Pmax': 'Paid Shopping',
        'partnerships': 'Partnerships',
        'other': 'Other',
        'Organic Social': 'Social',
        'Paid Social': 'Social'
    }
    
    orders_attribution_clean = orders_attribution.copy()
    orders_attribution_clean['default_channel_group'] = (
        orders_attribution_clean['default_channel_group']
        .replace(channel_mapping)
    )
    
    print("\nMarketing Channels after standardization:")
    print(orders_attribution_clean['default_channel_group'].value_counts())
    
    return orders_attribution_clean

def clean_discount_codes(orders_master):
    """Clean and standardize discount codes"""
    orders_master_clean = orders_master.copy()
    
    # Standardize discount codes
    orders_master_clean['DISCOUNT_CODE'] = (
        orders_master_clean['DISCOUNT_CODE']
        .str.strip()
        .str.upper()
        .fillna('(not set)')
    )
    
    # Group similar discount codes (example pattern)
    discount_mapping = {
        code: 'TREATS' for code in orders_master_clean['DISCOUNT_CODE']
        if 'TREAT' in str(code)
    }
    
    orders_master_clean['DISCOUNT_CODE'] = (
        orders_master_clean['DISCOUNT_CODE']
        .replace(discount_mapping)
    )
    
    print("\nTop 10 discount codes after cleaning:")
    print(orders_master_clean['DISCOUNT_CODE'].value_counts().head(10))
    
    return orders_master_clean

def main():
    orders_master, orders_sku, orders_attribution, periods_weeks = load_data()
    
    # Run existing checks
    check_data_quality(orders_master, orders_sku, orders_attribution, periods_weeks)
    check_price_anomalies(orders_sku)
    analyze_zero_price_items(orders_sku, orders_master)
    
    # Run new detailed analysis
    gift_inconsistencies = analyze_gift_inconsistencies(orders_sku)
    zero_price_patterns = analyze_zero_price_patterns(orders_sku, orders_master)
    problematic_skus = analyze_problematic_skus(orders_sku)

if __name__ == "__main__":
    main()
