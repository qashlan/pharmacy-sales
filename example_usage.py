"""Example usage of the pharmacy sales analytics system."""

import pandas as pd
from datetime import datetime

# Import analysis modules
from data_loader import DataLoader, load_sample_data
from sales_analysis import SalesAnalyzer
from customer_analysis import CustomerAnalyzer
from product_analysis import ProductAnalyzer
from rfm_analysis import RFMAnalyzer
from refill_prediction import RefillPredictor
from cross_sell_analysis import CrossSellAnalyzer
from ai_query import AIQueryEngine

def example_basic_usage():
    """Example: Basic data loading and analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60 + "\n")
    
    # Load sample data (replace with your CSV file path)
    print("Loading sample data...")
    df = load_sample_data()
    
    # Or load from file:
    # loader = DataLoader("your_sales_data.csv")
    # loader.load_data()
    # df = loader.preprocess_data()
    
    loader = DataLoader(None)
    loader.raw_data = df
    df = loader.preprocess_data()
    
    print(f"✓ Loaded {len(df)} records")
    print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"✓ Unique customers: {df['customer_name'].nunique()}")
    print(f"✓ Unique products: {df['item_name'].nunique()}")


def example_sales_analysis():
    """Example: Sales analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Sales Analysis")
    print("="*60 + "\n")
    
    df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = df
    df = loader.preprocess_data()
    
    # Initialize analyzer
    analyzer = SalesAnalyzer(df)
    
    # Get overall metrics
    print("Overall Metrics:")
    metrics = analyzer.get_overall_metrics()
    print(f"  Total Revenue: ${metrics['total_revenue']:,.2f}")
    print(f"  Total Orders: {metrics['total_orders']:,}")
    print(f"  Average Order Value: ${metrics['avg_order_value']:,.2f}")
    print(f"  Daily Average Revenue: ${metrics['daily_avg_revenue']:,.2f}")
    
    # Get top products
    print("\nTop 5 Products by Revenue:")
    top_products = analyzer.get_top_products(5, 'revenue')
    for idx, row in top_products.iterrows():
        print(f"  {row['item_name']}: ${row['revenue']:,.2f}")
    
    # Get top categories
    print("\nTop 3 Categories:")
    top_categories = analyzer.get_top_categories(3)
    for idx, row in top_categories.iterrows():
        print(f"  {row['category']}: ${row['revenue']:,.2f} ({row['revenue_pct']:.1f}%)")


def example_customer_analysis():
    """Example: Customer analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Customer Analysis")
    print("="*60 + "\n")
    
    df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = df
    df = loader.preprocess_data()
    
    # Initialize analyzer
    analyzer = CustomerAnalyzer(df)
    
    # Repeat purchase rate
    print("Customer Retention Metrics:")
    repeat_metrics = analyzer.get_repeat_purchase_rate()
    print(f"  Total Customers: {repeat_metrics['total_customers']:,}")
    print(f"  Repeat Customers: {repeat_metrics['repeat_customers']:,}")
    print(f"  Repeat Rate: {repeat_metrics['repeat_rate_pct']:.1f}%")
    print(f"  Average Customer LTV: ${repeat_metrics['avg_customer_ltv']:,.2f}")
    
    # Top customers
    print("\nTop 5 High-Value Customers:")
    top_customers = analyzer.get_high_value_customers(5)
    for idx, row in top_customers.iterrows():
        print(f"  {row['customer_name']}: ${row['total_spent']:,.2f} ({row['total_orders']} orders)")
    
    # Churn risk
    print("\nChurn Risk Analysis:")
    churn_risk = analyzer.get_churn_risk_customers(90)
    if len(churn_risk) > 0:
        print(f"  ⚠️  {len(churn_risk)} customers at risk of churning")
        print(f"  Total value at risk: ${churn_risk['total_spent'].sum():,.2f}")
    else:
        print("  ✓ No customers at risk of churning")


def example_product_analysis():
    """Example: Product performance analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Product Performance Analysis")
    print("="*60 + "\n")
    
    df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = df
    df = loader.preprocess_data()
    
    # Initialize analyzer
    analyzer = ProductAnalyzer(df)
    
    # Fast movers
    print("Top 5 Fast-Moving Products:")
    fast_movers = analyzer.get_fast_moving_products(5)
    for idx, row in fast_movers.iterrows():
        print(f"  {row['item_name']}: {row['sales_velocity']:.2f} units/day")
    
    # Slow movers
    print("\nTop 5 Slow-Moving Products:")
    slow_movers = analyzer.get_slow_moving_products(5)
    for idx, row in slow_movers.iterrows():
        print(f"  {row['item_name']}: {row['sales_velocity']:.2f} units/day " +
              f"({row['days_since_last_sale']} days since last sale)")
    
    # Inventory signals
    print("\nInventory Planning Signals:")
    signals = analyzer.get_inventory_planning_signals()
    signal_counts = signals['inventory_signal'].value_counts()
    for signal, count in signal_counts.items():
        print(f"  {signal}: {count} products")


def example_rfm_segmentation():
    """Example: RFM customer segmentation."""
    print("\n" + "="*60)
    print("EXAMPLE 5: RFM Customer Segmentation")
    print("="*60 + "\n")
    
    df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = df
    df = loader.preprocess_data()
    
    # Initialize analyzer
    analyzer = RFMAnalyzer(df)
    
    # Segment customers
    rfm_data = analyzer.segment_customers()
    
    # Get segment summary
    print("Customer Segment Distribution:")
    segment_summary = analyzer.get_segment_summary()
    for idx, row in segment_summary.iterrows():
        print(f"  {row['segment']}: {row['customer_count']} customers " +
              f"({row['revenue_pct']:.1f}% of revenue)")
    
    # VIP customers
    print("\nTop 5 VIP Customers:")
    vip = analyzer.get_vip_customers(5)
    for idx, row in vip.iterrows():
        print(f"  {row['customer_name']} ({row['segment']}): " +
              f"${row['monetary']:,.2f}, {row['frequency']} orders")
    
    # Recommendations for a segment
    print("\nRecommended Actions for 'Champions' Segment:")
    recommendations = analyzer.recommend_actions('Champions')
    for action in recommendations['actions']:
        print(f"  • {action}")


def example_refill_prediction():
    """Example: Refill prediction."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Refill Prediction")
    print("="*60 + "\n")
    
    df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = df
    df = loader.preprocess_data()
    
    # Initialize predictor
    predictor = RefillPredictor(df)
    predictor.calculate_purchase_intervals()
    
    # Summary stats
    print("Refill Prediction Summary:")
    summary = predictor.get_refill_summary_stats()
    print(f"  Customer-Product Pairs: {summary['total_refill_pairs']:,}")
    print(f"  Average Refill Interval: {summary['avg_refill_interval_days']:.1f} days")
    print(f"  Overdue Refills: {summary['num_overdue_refills']:,}")
    print(f"  Upcoming Refills (30 days): {summary['num_upcoming_refills_30d']:,}")
    
    # Overdue refills
    print("\nTop 5 Overdue Refills:")
    overdue = predictor.get_overdue_refills(7)
    if len(overdue) > 0:
        for idx, row in overdue.head(5).iterrows():
            print(f"  {row['customer_name']} - {row['item_name']}: " +
                  f"{row['days_overdue']} days overdue")
    else:
        print("  ✓ No overdue refills")
    
    # Upcoming refills
    print("\nUpcoming Refills (Next 14 Days):")
    upcoming = predictor.get_upcoming_refills(14)
    if len(upcoming) > 0:
        print(f"  {len(upcoming)} refills expected")
    else:
        print("  No refills expected in the next 14 days")


def example_cross_sell_analysis():
    """Example: Cross-sell analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Cross-Sell Analysis")
    print("="*60 + "\n")
    
    df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = df
    df = loader.preprocess_data()
    
    # Initialize analyzer
    analyzer = CrossSellAnalyzer(df)
    
    # Basket insights
    print("Market Basket Insights:")
    basket_insights = analyzer.get_customer_basket_insights()
    print(f"  Average Items per Basket: {basket_insights['avg_items_per_basket']:.2f}")
    print(f"  Average Basket Value: ${basket_insights['avg_basket_value']:.2f}")
    print(f"  Multi-Item Baskets: {basket_insights['pct_multi_item_baskets']:.1f}%")
    
    # Product bundles
    print("\nTop 3 Product Bundles:")
    bundles = analyzer.get_bundle_suggestions(2, 3, 3)
    if len(bundles) > 0:
        for idx, row in bundles.iterrows():
            items = ", ".join(row['bundle_items'])
            print(f"  Bundle {idx+1}: {items}")
            print(f"    Support: {row['support']:.1%}, Revenue: ${row['bundle_revenue']:,.2f}")
    else:
        print("  Not enough data for bundle analysis")
    
    # Product affinity
    print("\nTop 5 Product Associations:")
    affinity = analyzer.analyze_product_affinity()
    if len(affinity) > 0:
        for idx, row in affinity.head(5).iterrows():
            print(f"  {row['product_a']} + {row['product_b']}: " +
                  f"Lift {row['lift']:.2f}x")
    else:
        print("  Not enough data for affinity analysis")


def example_ai_queries():
    """Example: AI natural language queries."""
    print("\n" + "="*60)
    print("EXAMPLE 8: AI Natural Language Queries")
    print("="*60 + "\n")
    
    df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = df
    df = loader.preprocess_data()
    
    # Initialize query engine
    engine = AIQueryEngine(df)
    
    # Example queries
    queries = [
        "What is the total revenue?",
        "Show me the top 5 products",
        "Which customers are at risk of churning?",
        "What are the fast moving products?",
        "Show me overdue refills"
    ]
    
    for query in queries:
        print(f"\nQuery: \"{query}\"")
        result = engine.query(query)
        print(f"Answer: {result['answer']}")
        
        if 'recommendations' in result:
            print("Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")


def run_all_examples():
    """Run all examples."""
    example_basic_usage()
    example_sales_analysis()
    example_customer_analysis()
    example_product_analysis()
    example_rfm_segmentation()
    example_refill_prediction()
    example_cross_sell_analysis()
    example_ai_queries()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run individual examples or all at once
    
    # Run all examples
    run_all_examples()
    
    # Or run specific examples:
    # example_basic_usage()
    # example_sales_analysis()
    # example_ai_queries()

