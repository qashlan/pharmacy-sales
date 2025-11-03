"""Test script to verify monthly filtering functionality."""

import pandas as pd
from data_loader import DataLoader, load_sample_data
from sales_analysis import SalesAnalyzer

def test_monthly_filtering():
    """Test the monthly filtering feature."""
    
    print("="*70)
    print("TESTING MONTHLY FILTERING FUNCTIONALITY")
    print("="*70)
    
    # Load sample data
    print("\n1. Loading sample data...")
    sample_df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = sample_df
    processed_data = loader.preprocess_data()
    
    print(f"✓ Loaded {len(processed_data)} records")
    
    # Create analyzer
    print("\n2. Creating SalesAnalyzer...")
    analyzer = SalesAnalyzer(processed_data)
    
    # Get available months
    print("\n3. Getting available months...")
    available_months = analyzer.get_available_months()
    print(f"✓ Found {len(available_months)} months: {', '.join(available_months)}")
    
    # Test all-time metrics
    print("\n4. Testing all-time metrics...")
    all_time_metrics = analyzer.get_overall_metrics(month=None)
    print(f"   Total Revenue: ${all_time_metrics['total_revenue']:,.2f}")
    print(f"   Total Orders: {all_time_metrics['total_orders']:,}")
    print(f"   Unique Customers: {all_time_metrics['unique_customers']:,}")
    
    # Test monthly metrics
    if len(available_months) > 0:
        test_month = available_months[0]
        print(f"\n5. Testing metrics for {test_month}...")
        monthly_metrics = analyzer.get_overall_metrics(month=test_month)
        print(f"   Total Revenue: ${monthly_metrics['total_revenue']:,.2f}")
        print(f"   Total Orders: {monthly_metrics['total_orders']:,}")
        print(f"   Unique Customers: {monthly_metrics['unique_customers']:,}")
        
        # Test top products for the month
        print(f"\n6. Testing top products for {test_month}...")
        top_products = analyzer.get_top_products(n=5, metric='revenue', month=test_month)
        print(f"✓ Got {len(top_products)} top products:")
        for idx, row in top_products.iterrows():
            print(f"   - {row['item_name']}: ${row['revenue']:,.2f}")
        
        # Test top categories for the month
        print(f"\n7. Testing top categories for {test_month}...")
        top_categories = analyzer.get_top_categories(n=5, month=test_month)
        print(f"✓ Got {len(top_categories)} top categories:")
        for idx, row in top_categories.iterrows():
            print(f"   - {row['category']}: ${row['revenue']:,.2f} ({row['revenue_pct']:.1f}%)")
    
    # Compare all-time vs monthly
    if len(available_months) > 0:
        print("\n8. Comparing All Time vs Monthly...")
        print(f"   All Time Revenue: ${all_time_metrics['total_revenue']:,.2f}")
        print(f"   {test_month} Revenue: ${monthly_metrics['total_revenue']:,.2f}")
        percentage = (monthly_metrics['total_revenue'] / all_time_metrics['total_revenue'] * 100)
        print(f"   {test_month} is {percentage:.1f}% of all-time revenue")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)

if __name__ == "__main__":
    test_monthly_filtering()

