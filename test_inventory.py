"""Test script for inventory management functionality."""

import pandas as pd
import numpy as np
from datetime import datetime
from data_loader import DataLoader
from inventory_management import InventoryManager, create_sample_inventory
import config

def test_inventory_management():
    """Test inventory management features."""
    print("=" * 80)
    print("INVENTORY MANAGEMENT TEST")
    print("=" * 80)
    
    # Load sales data
    print("\n1. Loading sales data...")
    loader = DataLoader(str(config.BASE_DIR / "pharmacy_sales.xlsx"))
    sales_data = loader.load_data()
    sales_data = loader.preprocess_data()
    print(f"✓ Loaded {len(sales_data)} sales records")
    
    # Create sample inventory
    print("\n2. Creating sample inventory...")
    inventory_data = create_sample_inventory(sales_data)
    print(f"✓ Created inventory with {len(inventory_data)} items")
    
    # Display sample of inventory data
    print("\nSample inventory data:")
    print(inventory_data.head(10).to_string())
    
    # Initialize inventory manager
    print("\n3. Initializing inventory manager...")
    manager = InventoryManager(inventory_data, sales_data)
    print("✓ Inventory manager initialized")
    
    # Get inventory summary
    print("\n4. Getting inventory summary...")
    summary = manager.get_inventory_summary()
    print("\nInventory Summary:")
    print("-" * 60)
    print(f"Total Items:              {summary['total_items']:,}")
    print(f"Total Quantity on Hand:   {summary['total_quantity_on_hand']:,.0f}")
    print(f"Total Inventory Value:    ${summary['total_inventory_value']:,.2f}")
    print(f"Out of Stock:             {summary['items_out_of_stock']:,}")
    print(f"Urgent Reorder:           {summary['items_urgent_reorder']:,}")
    print(f"Reorder Soon:             {summary['items_reorder_soon']:,}")
    print(f"Monitor:                  {summary['items_to_monitor']:,}")
    print(f"OK:                       {summary['items_ok']:,}")
    print(f"Avg Days of Stock:        {summary['avg_days_of_stock']:.1f}")
    print(f"Items with No Sales:      {summary['items_with_no_sales']:,}")
    print(f"Fast Movers:              {summary['fast_movers']:,}")
    print(f"Slow Movers:              {summary['slow_movers']:,}")
    
    # Get reorder signals
    print("\n5. Analyzing reorder signals...")
    reorder_signals = manager.get_reorder_signals(lead_time_days=7, urgency_threshold_days=3)
    print(f"✓ Analyzed {len(reorder_signals)} items")
    
    # Show urgent items
    urgent = reorder_signals[
        reorder_signals['reorder_signal'].isin(['OUT_OF_STOCK', 'URGENT_REORDER'])
    ]
    
    if len(urgent) > 0:
        print(f"\n⚠️  {len(urgent)} URGENT ITEMS NEED REORDERING:")
        print("-" * 80)
        display_cols = ['item_name', 'quantity', 'reorder_signal', 'days_of_stock', 
                       'quantity_to_order', 'daily_sales_velocity']
        print(urgent[display_cols].head(10).to_string(index=False))
    else:
        print("\n✓ No urgent items to reorder!")
    
    # Get stockout risk
    print("\n6. Analyzing stockout risk...")
    stockout_risk = manager.get_stockout_risk(forecast_days=30)
    
    if len(stockout_risk) > 0:
        print(f"⚠️  {len(stockout_risk)} items at risk of stockout in next 30 days:")
        print("-" * 80)
        display_cols = ['item_name', 'quantity', 'predicted_stockout_days', 
                       'estimated_stockout_date', 'potential_lost_revenue']
        display_df = stockout_risk[
            [col for col in display_cols if col in stockout_risk.columns]
        ].head(10)
        
        if 'estimated_stockout_date' in display_df.columns:
            display_df['estimated_stockout_date'] = display_df['estimated_stockout_date'].dt.strftime('%Y-%m-%d')
        
        print(display_df.to_string(index=False))
    else:
        print("✓ No stockout risk in next 30 days!")
    
    # Get overstocked items
    print("\n7. Analyzing overstocked items...")
    overstocked = manager.get_overstocked_items(overstock_threshold_days=180)
    
    if len(overstocked) > 0:
        print(f"ℹ️  {len(overstocked)} overstocked items (>180 days of stock):")
        print("-" * 80)
        display_cols = ['item_name', 'quantity', 'days_of_stock', 
                       'daily_sales_velocity', 'overstock_value']
        display_df = overstocked[
            [col for col in display_cols if col in overstocked.columns]
        ].head(10)
        print(display_df.to_string(index=False))
    else:
        print("✓ No overstocked items!")
    
    # ABC Analysis
    print("\n8. Performing ABC analysis...")
    abc_df = manager.get_abc_analysis()
    
    abc_summary = abc_df.groupby('abc_class').agg({
        'item_code': 'count',
        'total_revenue': 'sum',
        'quantity': 'sum'
    }).reset_index()
    abc_summary.columns = ['ABC Class', 'Item Count', 'Total Revenue', 'Stock Quantity']
    
    print("\nABC Classification Summary:")
    print("-" * 80)
    print(abc_summary.to_string(index=False))
    
    # Category Analysis
    print("\n9. Analyzing by category...")
    category_df = manager.get_category_analysis()
    
    if len(category_df) > 0:
        print("\nCategory Analysis:")
        print("-" * 80)
        display_cols = ['category', 'num_items', 'stock_on_hand', 'total_sold', 
                       'total_revenue', 'inventory_turnover']
        display_df = category_df[
            [col for col in display_cols if col in category_df.columns]
        ]
        print(display_df.to_string(index=False))
    else:
        print("No category information available")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
    # Save sample outputs
    print("\n10. Saving sample outputs...")
    output_dir = config.OUTPUT_DIR / "inventory"
    output_dir.mkdir(exist_ok=True)
    
    reorder_signals.to_csv(output_dir / "reorder_signals.csv", index=False)
    print(f"✓ Saved reorder signals to {output_dir / 'reorder_signals.csv'}")
    
    if len(stockout_risk) > 0:
        stockout_risk.to_csv(output_dir / "stockout_risk.csv", index=False)
        print(f"✓ Saved stockout risk to {output_dir / 'stockout_risk.csv'}")
    
    abc_df.to_csv(output_dir / "abc_analysis.csv", index=False)
    print(f"✓ Saved ABC analysis to {output_dir / 'abc_analysis.csv'}")
    
    if len(category_df) > 0:
        category_df.to_csv(output_dir / "category_analysis.csv", index=False)
        print(f"✓ Saved category analysis to {output_dir / 'category_analysis.csv'}")
    
    # Save sample inventory template
    inventory_data.to_excel(output_dir / "sample_inventory.xlsx", index=False)
    print(f"✓ Saved sample inventory to {output_dir / 'sample_inventory.xlsx'}")
    
    print("\n✅ All outputs saved successfully!")


if __name__ == "__main__":
    try:
        test_inventory_management()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

