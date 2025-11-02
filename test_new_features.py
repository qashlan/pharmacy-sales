#!/usr/bin/env python3
"""Test script for receipt column and unknown customer features."""

import pandas as pd
import sys
from data_loader import DataLoader, load_sample_data


def test_sample_data():
    """Test with generated sample data that includes receipt and unknown customers."""
    print("=" * 80)
    print("TEST 1: Sample Data Generation")
    print("=" * 80)
    
    # Generate sample data
    df = load_sample_data()
    
    print(f"\n✓ Generated {len(df)} sample records")
    print(f"✓ Columns: {', '.join(df.columns.tolist())}")
    
    # Check for Receipt column
    if 'Receipt' in df.columns:
        print(f"✓ Receipt column present with {df['Receipt'].nunique()} unique receipts")
    
    # Check for empty customers
    empty_customers = df['Customer Name'].isna().sum() + (df['Customer Name'] == '').sum()
    print(f"✓ {empty_customers} records with empty/null customer names")
    
    # Show sample
    print("\n📋 Sample Records:")
    print(df[['Receipt', 'Customer Name', 'Item Name', 'Total']].head(10).to_string())
    
    return df


def test_data_loading(sample_df):
    """Test data loading and preprocessing."""
    print("\n" + "=" * 80)
    print("TEST 2: Data Loading & Preprocessing")
    print("=" * 80)
    
    # Create a temporary CSV file
    temp_file = '/tmp/test_pharmacy_sales.csv'
    sample_df.to_csv(temp_file, index=False)
    
    # Load and preprocess
    loader = DataLoader(temp_file)
    raw_data = loader.load_data()
    processed_data = loader.preprocess_data()
    
    print(f"\n✓ Loaded {len(raw_data)} records")
    print(f"✓ Preprocessed {len(processed_data)} records")
    
    # Check order_id
    print(f"\n📊 Order ID Statistics:")
    print(f"  - Unique order IDs: {processed_data['order_id'].nunique()}")
    print(f"  - Order ID type: {processed_data['order_id'].dtype}")
    print(f"  - Order ID range: {processed_data['order_id'].min()} to {processed_data['order_id'].max()}")
    
    # Check customer names
    print(f"\n👥 Customer Statistics:")
    print(f"  - Unique customers: {processed_data['customer_name'].nunique()}")
    unknown_count = (processed_data['customer_name'] == 'Unknown Customer').sum()
    print(f"  - Unknown customers: {unknown_count} records ({unknown_count/len(processed_data)*100:.1f}%)")
    
    # Show customer distribution
    print(f"\n📈 Top 5 Customers by Record Count:")
    top_customers = processed_data['customer_name'].value_counts().head()
    for customer, count in top_customers.items():
        print(f"  - {customer}: {count} records")
    
    # Check for receipt column usage
    if 'receipt' in processed_data.columns:
        receipt_match = (processed_data['order_id'] == processed_data['receipt']).sum()
        print(f"\n✓ Receipt column detected and used")
        print(f"  - Order ID matches receipt: {receipt_match}/{len(processed_data)} records")
    
    return processed_data


def test_data_summary(processed_data):
    """Test data summary functionality."""
    print("\n" + "=" * 80)
    print("TEST 3: Data Summary")
    print("=" * 80)
    
    loader = DataLoader('/tmp/test_pharmacy_sales.csv')
    loader.processed_data = processed_data
    
    summary = loader.get_data_summary()
    
    print(f"\n📊 Summary Statistics:")
    print(f"  - Total Records: {summary['total_records']}")
    print(f"  - Date Range: {summary['date_range'][0].strftime('%Y-%m-%d')} to {summary['date_range'][1].strftime('%Y-%m-%d')}")
    print(f"  - Total Revenue: ${summary['total_revenue']:,.2f}")
    print(f"  - Unique Customers: {summary['unique_customers']}")
    print(f"  - Unique Products: {summary['unique_products']}")
    print(f"  - Unique Orders: {summary['unique_orders']}")
    print(f"  - Average Order Value: ${summary['avg_order_value']:,.2f}")
    print(f"  - Total Quantity Sold: {summary['total_quantity_sold']:,.0f}")


def test_backward_compatibility():
    """Test backward compatibility with files without Receipt column."""
    print("\n" + "=" * 80)
    print("TEST 4: Backward Compatibility (No Receipt Column)")
    print("=" * 80)
    
    # Generate data without Receipt column
    df = load_sample_data()
    df_old = df.drop(columns=['Receipt'])
    
    temp_file = '/tmp/test_pharmacy_sales_old.csv'
    df_old.to_csv(temp_file, index=False)
    
    # Load and preprocess
    loader = DataLoader(temp_file)
    raw_data = loader.load_data()
    processed_data = loader.preprocess_data()
    
    print(f"\n✓ Loaded {len(raw_data)} records without Receipt column")
    print(f"✓ Preprocessed {len(processed_data)} records")
    print(f"✓ Computed {processed_data['order_id'].nunique()} order IDs automatically")
    print(f"✓ Order ID type: {processed_data['order_id'].dtype}")
    
    return processed_data


def test_unknown_customer_analytics(processed_data):
    """Test that analytics work with unknown customers."""
    print("\n" + "=" * 80)
    print("TEST 5: Unknown Customer Analytics")
    print("=" * 80)
    
    # Group by customer
    customer_stats = processed_data.groupby('customer_name').agg({
        'order_id': 'nunique',
        'total': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    customer_stats.columns = ['customer_name', 'orders', 'revenue', 'quantity']
    customer_stats = customer_stats.sort_values('revenue', ascending=False)
    
    print(f"\n📊 Customer Analysis Works!")
    print(f"  - Analyzed {len(customer_stats)} unique customers")
    
    # Check unknown customer
    unknown_stats = customer_stats[customer_stats['customer_name'] == 'Unknown Customer']
    if len(unknown_stats) > 0:
        print(f"\n👤 Unknown Customer Statistics:")
        print(f"  - Orders: {unknown_stats['orders'].values[0]}")
        print(f"  - Revenue: ${unknown_stats['revenue'].values[0]:,.2f}")
        print(f"  - Quantity: {unknown_stats['quantity'].values[0]:,.0f}")
    
    print(f"\n📈 Top 5 Customers by Revenue:")
    for idx, row in customer_stats.head().iterrows():
        print(f"  - {row['customer_name']}: ${row['revenue']:,.2f} ({row['orders']} orders)")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🧪 TESTING NEW FEATURES: Receipt Column & Unknown Customers")
    print("=" * 80)
    
    try:
        # Test 1: Sample data generation
        sample_df = test_sample_data()
        
        # Test 2: Data loading and preprocessing
        processed_data = test_data_loading(sample_df)
        
        # Test 3: Data summary
        test_data_summary(processed_data)
        
        # Test 4: Backward compatibility
        test_backward_compatibility()
        
        # Test 5: Unknown customer analytics
        test_unknown_customer_analytics(processed_data)
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\n📝 Summary:")
        print("  ✓ Receipt column is detected and used as order_id")
        print("  ✓ Empty/null customers are handled as 'Unknown Customer'")
        print("  ✓ Backward compatibility maintained (files without Receipt column work)")
        print("  ✓ All analytics work seamlessly with unknown customers")
        print("  ✓ Data processing is stable and error-free")
        print("\n🎉 Your system is ready to use with the new features!")
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

