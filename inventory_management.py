"""Inventory management module with reorder signals based on sales analysis."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class InventoryManager:
    """Manages inventory levels and provides reorder recommendations based on sales velocity."""
    
    def __init__(self, inventory_data: pd.DataFrame, sales_data: pd.DataFrame):
        """
        Initialize inventory manager.
        
        Args:
            inventory_data: DataFrame with columns: item_code, item_name, selling_price, 
                           units, pieces, quantity, category
            sales_data: Preprocessed sales DataFrame
        """
        self.inventory_data = inventory_data.copy()
        self.sales_data = sales_data.copy()
        
        # Standardize inventory column names
        self._standardize_inventory_columns()
        
        # Calculate sales metrics
        self.sales_metrics = self._calculate_sales_metrics()
        
        # Merge inventory with sales data
        self.enriched_inventory = self._enrich_inventory()
        
    def _standardize_inventory_columns(self):
        """
        Standardize inventory column names.
        
        IMPORTANT - Understanding Units, Pieces, and Quantity:
        ======================================================
        - **Units**: Number of full units/boxes in stock (integer)
        - **Pieces**: Number of loose pieces in stock (integer)
        - **Quantity**: Total effective quantity - AUTHORITATIVE measure (can be fractional)
        
        Examples:
        ---------
        1. Units=1, Pieces=1, Quantity=1.50
           → We have 1 full unit + 1 loose piece = 1.50 total units
        
        2. Units=0, Pieces=1, Quantity=0.50
           → We have 0 full units + 1 loose piece = 0.50 units
        
        The system uses **Quantity** as the authoritative stock level for all calculations.
        Units and Pieces are informational/display purposes only.
        """
        # Common column name variations
        column_map = {
            'Item Code': 'item_code',
            'Item Name': 'item_name',
            'Iten Name': 'item_name',  # Handle typo
            'Selling Price': 'selling_price',
            'Units': 'units',
            'Pieces': 'pieces',
            'Quantity': 'quantity',
            'Category': 'category'
        }
        
        # Apply mapping
        for original, standard in column_map.items():
            if original in self.inventory_data.columns:
                self.inventory_data.rename(columns={original: standard}, inplace=True)
        
        # Case-insensitive fallback
        self.inventory_data.columns = [col.lower().replace(' ', '_') for col in self.inventory_data.columns]
        
        # Ensure required columns exist
        required_cols = ['item_code', 'item_name', 'quantity']
        missing = [col for col in required_cols if col not in self.inventory_data.columns]
        if missing:
            raise ValueError(f"Missing required inventory columns: {missing}")
        
        # Convert quantity to numeric
        self.inventory_data['quantity'] = pd.to_numeric(
            self.inventory_data['quantity'], errors='coerce'
        ).fillna(0)
        
        # Ensure item_code is string
        self.inventory_data['item_code'] = self.inventory_data['item_code'].astype(str)
        
        print(f"✓ Loaded inventory: {len(self.inventory_data)} items")
        
    def _calculate_sales_metrics(self) -> pd.DataFrame:
        """Calculate sales velocity and patterns for each product."""
        # Only use non-refund sales for velocity calculation
        sales_df = self.sales_data[~self.sales_data['is_refund']].copy()
        
        # Get date range
        date_range_days = (sales_df['date'].max() - sales_df['date'].min()).days
        if date_range_days == 0:
            date_range_days = 1
        
        # Calculate metrics per product
        metrics = sales_df.groupby('item_code').agg({
            'quantity': ['sum', 'mean', 'std', 'count'],
            'total': 'sum',
            'date': ['min', 'max']
        }).reset_index()
        
        # Flatten column names
        metrics.columns = ['item_code', 'total_quantity_sold', 'avg_quantity_per_order', 
                          'std_quantity', 'num_orders', 'total_revenue',
                          'first_sale_date', 'last_sale_date']
        
        # Calculate sales velocity (units per day)
        metrics['days_on_sale'] = (metrics['last_sale_date'] - metrics['first_sale_date']).dt.days + 1
        metrics['days_on_sale'] = metrics['days_on_sale'].clip(lower=1)
        metrics['daily_sales_velocity'] = metrics['total_quantity_sold'] / metrics['days_on_sale']
        
        # Calculate weekly and monthly velocity
        metrics['weekly_sales_velocity'] = metrics['daily_sales_velocity'] * 7
        metrics['monthly_sales_velocity'] = metrics['daily_sales_velocity'] * 30
        
        # Calculate days since last sale
        latest_date = sales_df['date'].max()
        metrics['days_since_last_sale'] = (latest_date - metrics['last_sale_date']).dt.days
        
        # Calculate sales consistency (coefficient of variation)
        metrics['sales_consistency'] = 1 - (metrics['std_quantity'] / metrics['avg_quantity_per_order']).fillna(0)
        metrics['sales_consistency'] = metrics['sales_consistency'].clip(0, 1)
        
        return metrics
    
    def _enrich_inventory(self) -> pd.DataFrame:
        """Merge inventory with sales metrics."""
        enriched = self.inventory_data.merge(
            self.sales_metrics,
            on='item_code',
            how='left'
        )
        
        # Fill NaN for items with no sales history
        enriched['total_quantity_sold'] = enriched['total_quantity_sold'].fillna(0)
        enriched['daily_sales_velocity'] = enriched['daily_sales_velocity'].fillna(0)
        enriched['weekly_sales_velocity'] = enriched['weekly_sales_velocity'].fillna(0)
        enriched['monthly_sales_velocity'] = enriched['monthly_sales_velocity'].fillna(0)
        enriched['num_orders'] = enriched['num_orders'].fillna(0)
        enriched['sales_consistency'] = enriched['sales_consistency'].fillna(0)
        enriched['days_since_last_sale'] = enriched['days_since_last_sale'].fillna(999)
        
        return enriched
    
    def calculate_reorder_points(self, 
                                 lead_time_days: int = 7,
                                 service_level: float = 0.95,
                                 safety_stock_factor: float = 1.5) -> pd.DataFrame:
        """
        Calculate reorder points and safety stock for each item.
        
        Args:
            lead_time_days: Number of days between ordering and receiving stock
            service_level: Desired service level (e.g., 0.95 = 95% of orders fulfilled)
            safety_stock_factor: Multiplier for safety stock calculation
            
        Returns:
            DataFrame with reorder recommendations
        """
        df = self.enriched_inventory.copy()
        
        # Calculate lead time demand
        df['lead_time_demand'] = df['daily_sales_velocity'] * lead_time_days
        
        # Calculate safety stock
        # For items with consistent sales, use lower safety stock
        # For items with variable sales, use higher safety stock
        df['safety_stock'] = (
            df['lead_time_demand'] * safety_stock_factor * (1 - df['sales_consistency'] * 0.5)
        )
        
        # Calculate reorder point
        df['reorder_point'] = df['lead_time_demand'] + df['safety_stock']
        
        # Calculate days of stock remaining
        df['days_of_stock'] = np.where(
            df['daily_sales_velocity'] > 0,
            df['quantity'] / df['daily_sales_velocity'],
            999  # If no sales, assume plenty of stock
        )
        
        # Calculate optimal order quantity (Economic Order Quantity simplified)
        # Order enough for ~30 days or minimum batch size
        df['optimal_order_quantity'] = np.maximum(
            df['monthly_sales_velocity'],
            10  # Minimum order quantity
        )
        
        # Round to reasonable numbers
        df['reorder_point'] = df['reorder_point'].round(0)
        df['safety_stock'] = df['safety_stock'].round(0)
        df['optimal_order_quantity'] = df['optimal_order_quantity'].round(0)
        df['days_of_stock'] = df['days_of_stock'].round(1)
        
        return df
    
    def get_reorder_signals(self, 
                           lead_time_days: int = 7,
                           urgency_threshold_days: int = 3) -> pd.DataFrame:
        """
        Get items that need to be reordered with urgency levels.
        
        Args:
            lead_time_days: Lead time for ordering
            urgency_threshold_days: Days threshold for urgent reorders
            
        Returns:
            DataFrame with reorder recommendations sorted by urgency
        """
        df = self.calculate_reorder_points(lead_time_days=lead_time_days)
        
        # Determine reorder signal
        def get_signal(row):
            if row['quantity'] <= 0:
                return 'OUT_OF_STOCK'
            elif row['quantity'] < row['reorder_point']:
                if row['days_of_stock'] <= urgency_threshold_days:
                    return 'URGENT_REORDER'
                else:
                    return 'REORDER_SOON'
            elif row['quantity'] < row['reorder_point'] * 1.5:
                return 'MONITOR'
            else:
                return 'OK'
        
        df['reorder_signal'] = df.apply(get_signal, axis=1)
        
        # Calculate quantity to order
        df['quantity_to_order'] = np.maximum(
            0,
            df['optimal_order_quantity'] + df['reorder_point'] - df['quantity']
        ).round(0)
        
        # Add priority score (higher = more urgent)
        signal_priority = {
            'OUT_OF_STOCK': 5,
            'URGENT_REORDER': 4,
            'REORDER_SOON': 3,
            'MONITOR': 2,
            'OK': 1
        }
        df['priority_score'] = df['reorder_signal'].map(signal_priority)
        
        # Sort by priority and sales velocity
        df = df.sort_values(['priority_score', 'daily_sales_velocity'], ascending=[False, False])
        
        return df
    
    def get_overstocked_items(self, 
                             overstock_threshold_days: int = 180) -> pd.DataFrame:
        """
        Identify potentially overstocked items (slow movers with high inventory).
        
        Args:
            overstock_threshold_days: Days of stock threshold for overstock
            
        Returns:
            DataFrame with potentially overstocked items
        """
        df = self.calculate_reorder_points()
        
        # Items with more than threshold days of stock
        overstocked = df[df['days_of_stock'] > overstock_threshold_days].copy()
        
        # Calculate overstock value
        if 'selling_price' in overstocked.columns:
            overstocked['overstock_value'] = (
                overstocked['quantity'] * 
                pd.to_numeric(overstocked['selling_price'], errors='coerce').fillna(0)
            )
        
        # Sort by days of stock (highest first)
        overstocked = overstocked.sort_values('days_of_stock', ascending=False)
        
        return overstocked
    
    def get_stockout_risk(self, forecast_days: int = 30) -> pd.DataFrame:
        """
        Predict which items are at risk of stockout in the forecast period.
        
        Args:
            forecast_days: Number of days to forecast
            
        Returns:
            DataFrame with stockout risk analysis
        """
        df = self.calculate_reorder_points()
        
        # Predict stockout date
        df['predicted_stockout_days'] = np.where(
            df['daily_sales_velocity'] > 0,
            df['quantity'] / df['daily_sales_velocity'],
            999
        )
        
        # Items at risk within forecast period
        at_risk = df[df['predicted_stockout_days'] <= forecast_days].copy()
        
        # Calculate estimated stockout date
        today = datetime.now().date()
        at_risk['estimated_stockout_date'] = pd.to_datetime(today) + pd.to_timedelta(
            at_risk['predicted_stockout_days'], unit='D'
        )
        
        # Calculate potential lost revenue
        if 'selling_price' in at_risk.columns:
            # Revenue lost per day after stockout until end of forecast period
            days_out_of_stock = forecast_days - at_risk['predicted_stockout_days']
            at_risk['potential_lost_revenue'] = (
                days_out_of_stock * 
                at_risk['daily_sales_velocity'] * 
                pd.to_numeric(at_risk['selling_price'], errors='coerce').fillna(0)
            )
        
        # Sort by stockout date (soonest first)
        at_risk = at_risk.sort_values('predicted_stockout_days')
        
        return at_risk
    
    def get_inventory_summary(self) -> Dict:
        """Get overall inventory statistics."""
        df = self.calculate_reorder_points()
        
        # Get reorder signals
        signals_df = self.get_reorder_signals()
        signals = signals_df['reorder_signal'].value_counts().to_dict()
        
        # Calculate inventory value
        total_inventory_value = 0
        if 'selling_price' in df.columns:
            total_inventory_value = (
                df['quantity'] * 
                pd.to_numeric(df['selling_price'], errors='coerce').fillna(0)
            ).sum()
        
        return {
            'total_items': len(df),
            'total_quantity_on_hand': df['quantity'].sum(),
            'total_inventory_value': total_inventory_value,
            'items_out_of_stock': signals.get('OUT_OF_STOCK', 0),
            'items_urgent_reorder': signals.get('URGENT_REORDER', 0),
            'items_reorder_soon': signals.get('REORDER_SOON', 0),
            'items_to_monitor': signals.get('MONITOR', 0),
            'items_ok': signals.get('OK', 0),
            'avg_days_of_stock': df['days_of_stock'].replace([np.inf, 999], np.nan).mean(),
            'items_with_no_sales': len(df[df['total_quantity_sold'] == 0]),
            'fast_movers': len(df[df['daily_sales_velocity'] > df['daily_sales_velocity'].quantile(0.75)]),
            'slow_movers': len(df[df['daily_sales_velocity'] < df['daily_sales_velocity'].quantile(0.25)])
        }
    
    def get_abc_analysis(self) -> pd.DataFrame:
        """
        Perform ABC analysis on inventory based on sales revenue.
        
        A items: Top 20% items generating ~80% revenue
        B items: Next 30% items generating ~15% revenue  
        C items: Remaining 50% items generating ~5% revenue
        """
        df = self.calculate_reorder_points()
        
        # Sort by total revenue
        df = df.sort_values('total_revenue', ascending=False)
        
        # Calculate cumulative revenue percentage
        df['cumulative_revenue'] = df['total_revenue'].cumsum()
        total_revenue = df['total_revenue'].sum()
        df['cumulative_revenue_pct'] = (df['cumulative_revenue'] / total_revenue * 100)
        
        # Assign ABC class
        def assign_class(pct):
            if pct <= 80:
                return 'A'
            elif pct <= 95:
                return 'B'
            else:
                return 'C'
        
        df['abc_class'] = df['cumulative_revenue_pct'].apply(assign_class)
        
        return df
    
    def get_category_analysis(self) -> pd.DataFrame:
        """Analyze inventory and sales by category."""
        if 'category' not in self.enriched_inventory.columns:
            return pd.DataFrame()
        
        df = self.calculate_reorder_points()
        
        # Calculate current inventory value for each item
        if 'selling_price' in df.columns:
            df['inventory_value'] = (
                df['quantity'] * 
                pd.to_numeric(df['selling_price'], errors='coerce').fillna(0)
            )
        else:
            df['inventory_value'] = 0
        
        # Group by category
        category_stats = df.groupby('category').agg({
            'quantity': 'sum',
            'total_quantity_sold': 'sum',
            'total_revenue': 'sum',
            'item_code': 'count',
            'inventory_value': 'sum'
        }).reset_index()
        
        category_stats.columns = ['category', 'stock_on_hand', 'total_sold', 
                                  'total_revenue', 'num_items', 'current_value']
        
        # Calculate inventory turnover
        category_stats['inventory_turnover'] = np.where(
            category_stats['stock_on_hand'] > 0,
            category_stats['total_sold'] / category_stats['stock_on_hand'],
            0
        )
        
        # Sort by revenue
        category_stats = category_stats.sort_values('total_revenue', ascending=False)
        
        return category_stats


def load_inventory_from_file(file_path: str) -> pd.DataFrame:
    """
    Load inventory data from Excel or CSV file.
    
    Args:
        file_path: Path to inventory file
        
    Returns:
        DataFrame with inventory data
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or Excel.")
        
        print(f"✓ Loaded inventory file: {len(df)} items")
        return df
        
    except Exception as e:
        raise Exception(f"Error loading inventory file: {str(e)}")


def create_sample_inventory(sales_data: pd.DataFrame) -> pd.DataFrame:
    """
    Create sample inventory data based on sales data.
    
    Args:
        sales_data: Sales DataFrame
        
    Returns:
        Sample inventory DataFrame
    """
    # Get unique products from sales
    products = sales_data.groupby(['item_code', 'item_name']).agg({
        'selling_price': 'mean',
        'category': 'first',
        'quantity': 'sum'
    }).reset_index()
    
    # Generate random inventory quantities
    np.random.seed(42)
    products['quantity'] = (products['quantity'] * np.random.uniform(0.1, 2.0, len(products))).round(0)
    
    # Add units and pieces (optional)
    products['units'] = products['quantity'].astype(int)
    products['pieces'] = 0
    
    # Ensure proper column order
    inventory = products[['item_code', 'item_name', 'selling_price', 
                         'units', 'pieces', 'quantity', 'category']].copy()
    
    print(f"✓ Generated sample inventory: {len(inventory)} items")
    return inventory

