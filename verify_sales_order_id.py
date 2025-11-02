#!/usr/bin/env python3
"""
Verify Order ID Usage in Sales Analysis

This script verifies whether the Sales Analysis is using the Receipt column
or computed order IDs, and clarifies the "weird order_id" values in anomaly detection.
"""

from data_loader import DataLoader
from sales_analysis import SalesAnalyzer
import config
import pandas as pd


def verify_sales_order_id():
    """Verify order_id usage in sales analysis."""
    
    print("="*70)
    print("SALES ANALYSIS - ORDER ID VERIFICATION")
    print("="*70)
    
    # Load and preprocess data
    print("\n1️⃣ Loading data...")
    loader = DataLoader(config.DATA_FILE)
    data = loader.load_data()
    
    # Check for receipt column BEFORE preprocessing
    has_receipt = 'Receipt' in data.columns or 'receipt' in data.columns
    print(f"\n   Receipt column in raw data: {'✅ YES' if has_receipt else '❌ NO'}")
    
    # Preprocess
    data = loader.preprocess_data()
    
    # Initialize sales analyzer (watch for automatic verification)
    print("\n2️⃣ Initializing Sales Analyzer...")
    print("   (Watch for automatic order_id verification)")
    analyzer = SalesAnalyzer(data)
    
    # Detailed verification
    print("\n3️⃣ Detailed Order ID Verification:")
    analyzer.print_order_id_verification()
    
    # Explain anomaly detection
    print("\n4️⃣ Understanding Anomaly Detection Output:")
    print("="*70)
    print("\n❓ COMMON CONFUSION: 'Weird order_id' in Anomaly Detection")
    print("\n📌 EXPLANATION:")
    print("   The anomaly detection output has a column called 'num_orders'")
    print("   (previously labeled 'order_id' which was confusing).")
    print("\n   This column contains:")
    print("   ✓ The COUNT of unique orders per day")
    print("   ✗ NOT the actual order_id values")
    print("\n   Example:")
    print("   Date       | num_orders | total    | is_anomaly")
    print("   2024-01-01 | 45         | $1,200   | False")
    print("   2024-01-02 | 123        | $3,500   | True  ← Anomaly!")
    print("   2024-01-03 | 38         | $980     | False")
    print("\n   The 'num_orders' shows there were 45 orders on Jan 1, 123 on Jan 2, etc.")
    print("   Jan 2 is flagged as anomaly because 123 orders is unusual.")
    print("="*70)
    
    # Test anomaly detection
    print("\n5️⃣ Testing Anomaly Detection:")
    print("   Detecting anomalies in daily sales...")
    
    try:
        anomalies = analyzer.detect_anomalies(contamination=0.05)
        
        print(f"\n   ✅ Anomaly detection complete!")
        print(f"   • Total days analyzed: {len(anomalies)}")
        print(f"   • Days flagged as anomalies: {anomalies['is_anomaly'].sum()}")
        
        # Show column explanation
        print(f"\n   📋 Output columns explained:")
        print(f"      • date: The day being analyzed")
        print(f"      • total: Total revenue for that day")
        print(f"      • num_orders: COUNT of unique orders (NOT order_id values!)")
        print(f"      • quantity: Total items sold")
        print(f"      • is_anomaly: True if day is unusual")
        
        # Show sample
        print(f"\n   🔍 Sample anomaly detection output:")
        sample = anomalies[['date', 'total', 'num_orders', 'quantity', 'is_anomaly']].head()
        print(sample.to_string(index=False))
        
        # Show actual anomalies if found
        actual_anomalies = anomalies[anomalies['is_anomaly']]
        if len(actual_anomalies) > 0:
            print(f"\n   ⚠ Anomalies detected:")
            for _, row in actual_anomalies.head(3).iterrows():
                print(f"\n      Date: {row['date'].date()}")
                print(f"      Revenue: ${row['total']:,.2f}")
                print(f"      Orders: {int(row['num_orders'])} (count of unique orders)")
                print(f"      Items: {int(row['quantity'])}")
                print(f"      Why anomaly: Unusual combination of values")
    
    except Exception as e:
        print(f"   ⚠ Error detecting anomalies: {str(e)}")
    
    # Compare with actual order_id values
    print("\n6️⃣ Actual Order ID Values in Data:")
    print("="*70)
    
    sample_order_ids = data['order_id'].unique()[:10]
    print(f"\n   First 10 actual order_id values in your data:")
    for i, order_id in enumerate(sample_order_ids, 1):
        num_items = len(data[data['order_id'] == order_id])
        print(f"      {i}. order_id: {order_id} ({num_items} item{'s' if num_items > 1 else ''})")
    
    print(f"\n   These are the ACTUAL order_id values.")
    print(f"   In anomaly detection, we COUNT these per day, not show them directly.")
    print("="*70)
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    info = analyzer.verify_order_id_usage()
    
    if info['source'] == "Receipt column":
        print("\n✅ Sales Analysis is using RECEIPT-based order IDs")
        print(f"   • Order IDs come from Receipt column in your data")
        print(f"   • Order ID range: {info['min_order_id']} to {info['max_order_id']}")
        print(f"   • This is accurate and reliable")
    else:
        print("\n⚠ Sales Analysis is using COMPUTED order IDs")
        print(f"   • No Receipt column found in data")
        print(f"   • Orders grouped by: Customer + Time Window (30 min)")
        print(f"   • Order IDs are sequential: {info['min_order_id']} to {info['max_order_id']}")
        print(f"\n   💡 To use Receipt column:")
        print(f"      1. Ensure your data has a 'Receipt' column")
        print(f"      2. Reload and preprocess the data")
        print(f"      3. Order IDs will then come from Receipt numbers")
    
    print(f"\n📊 Order Statistics:")
    print(f"   • Total unique orders: {info['unique_orders']:,}")
    print(f"   • Multi-item orders: {info['multi_item_orders']:,} ({info['multi_item_percentage']:.1f}%)")
    
    print("\n🔍 About Anomaly Detection:")
    print("   • Column 'num_orders' = COUNT of orders per day")
    print("   • NOT the actual order_id values")
    print("   • This is by design - we're analyzing daily patterns")
    
    print("\n" + "="*70 + "\n")


def show_anomaly_example():
    """Show a detailed example of anomaly detection output."""
    
    print("\n" + "="*70)
    print("EXAMPLE: Understanding Anomaly Detection Output")
    print("="*70)
    
    # Create example data
    example = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=5),
        'total': [1200, 3500, 980, 1150, 1100],
        'num_orders': [45, 123, 38, 42, 40],
        'quantity': [150, 420, 130, 145, 138],
        'is_anomaly': [False, True, False, False, False]
    })
    
    print("\nExample output from detect_anomalies():")
    print(example.to_string(index=False))
    
    print("\n📌 Interpretation:")
    print("\n   Date: 2024-01-02 is flagged as anomaly")
    print("   Why:")
    print("      • Total revenue: $3,500 (much higher than other days)")
    print("      • num_orders: 123 (much higher than usual 40-45)")
    print("      • quantity: 420 (much higher than usual 130-150)")
    print("\n   What num_orders means:")
    print("      • On 2024-01-01: There were 45 unique orders")
    print("      • On 2024-01-02: There were 123 unique orders (unusual!)")
    print("      • On 2024-01-03: There were 38 unique orders")
    print("\n   The actual order_id values (like 1001, 1002, etc.) are NOT shown here.")
    print("   We only show the COUNT of how many orders occurred each day.")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Run verification
    verify_sales_order_id()
    
    # Show example
    show_anomaly_example()
    
    print("\n💡 KEY TAKEAWAYS:")
    print("   1. Check if your data has a Receipt column for accurate order grouping")
    print("   2. Anomaly detection shows COUNT of orders per day, not order_id values")
    print("   3. 'num_orders' = number of unique orders on that day")
    print("   4. Use print_order_id_verification() to verify order_id source anytime")
    print("\n")


