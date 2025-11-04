"""Product performance analysis module."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class ProductAnalyzer:
    """Analyzes product performance, trends, and inventory signals."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize product analyzer.
        
        Args:
            data: Preprocessed sales DataFrame
        """
        # Filter out service items - they're not physical products
        # Services are excluded from all product analyses (ABC, velocity, lifecycle, etc.)
        if 'is_service' in data.columns:
            self.data = data[~data['is_service']].copy()
            num_services_excluded = data['is_service'].sum()
            if num_services_excluded > 0:
                print(f"ℹ️  Product Analysis: Excluded {num_services_excluded} service transactions from product metrics")
        else:
            self.data = data
        
        self.current_date = self.data['date'].max()
        # Cache for expensive computations
        self._product_summary_cache: Optional[pd.DataFrame] = None
        
    def get_product_summary(self) -> pd.DataFrame:
        """Get comprehensive summary for each product with refund handling. (CACHED)"""
        # Return cached result if available
        if self._product_summary_cache is not None:
            return self._product_summary_cache
        
        # Separate sales from refunds
        sales_data = self.data[~self.data['is_refund']]
        refunds_data = self.data[self.data['is_refund']]
        
        # Calculate sales metrics (include units and pieces if available)
        agg_dict = {
            'order_id': 'nunique',
            'quantity': 'sum',
            'total': 'sum',
            'customer_name': 'nunique',
            'date': ['min', 'max']
        }
        
        # Add units and pieces if they exist
        if 'units' in sales_data.columns:
            agg_dict['units'] = 'sum'
        if 'pieces' in sales_data.columns:
            agg_dict['pieces'] = 'sum'
        
        product_stats = sales_data.groupby(['item_code', 'item_name', 'category']).agg(agg_dict).reset_index()
        
        # Flatten column names - they come out in the order they're in the dict
        # Order after groupby: order_id, quantity, total, customer_name, date(min), date(max), units*, pieces*
        # * = optional, added at the end if they exist
        
        col_names = ['item_code', 'item_name', 'category', 'orders', 'quantity_sold', 
                    'gross_revenue', 'unique_customers', 'first_sale', 'last_sale']
        
        # Units and pieces were added AFTER date in the dict, so they come at the END
        if 'units' in agg_dict:
            col_names.append('units_sold')
        
        if 'pieces' in agg_dict:
            col_names.append('pieces_sold')
        
        product_stats.columns = col_names
        
        # Calculate refund metrics per product
        product_refunds = refunds_data.groupby(['item_code', 'item_name', 'category']).agg({
            'total': lambda x: abs(x.sum()),
            'quantity': lambda x: abs(x.sum()),
            'order_id': 'nunique'
        }).reset_index()
        product_refunds.columns = ['item_code', 'item_name', 'category', 'refund_amount', 'refund_quantity', 'refund_orders']
        
        # Merge refund data
        product_stats = product_stats.merge(
            product_refunds[['item_code', 'refund_amount', 'refund_quantity', 'refund_orders']], 
            on='item_code', 
            how='left'
        )
        product_stats['refund_amount'] = product_stats['refund_amount'].fillna(0)
        product_stats['refund_quantity'] = product_stats['refund_quantity'].fillna(0)
        product_stats['refund_orders'] = product_stats['refund_orders'].fillna(0).astype(int)
        
        # Calculate net metrics
        product_stats['revenue'] = product_stats['gross_revenue'] - product_stats['refund_amount']
        product_stats['net_quantity'] = product_stats['quantity_sold'] - product_stats['refund_quantity']
        
        # Calculate refund rate
        product_stats['refund_rate_pct'] = (
            product_stats['refund_amount'] / product_stats['gross_revenue'] * 100
        ).fillna(0)
        
        # Calculate metrics
        product_stats['avg_price'] = product_stats['revenue'] / product_stats['net_quantity']
        product_stats['avg_quantity_per_order'] = product_stats['net_quantity'] / product_stats['orders']
        
        # Days on market
        product_stats['days_on_market'] = (
            product_stats['last_sale'] - product_stats['first_sale']
        ).dt.days + 1
        
        # Days since last sale
        product_stats['days_since_last_sale'] = (
            self.current_date - product_stats['last_sale']
        ).dt.days
        
        # Sales velocity (units per day) - using net quantity
        product_stats['sales_velocity'] = (
            product_stats['net_quantity'] / product_stats['days_on_market']
        ).replace([np.inf, -np.inf], 0)
        
        result = product_stats.sort_values('revenue', ascending=False)
        
        # Cache the result
        self._product_summary_cache = result
        
        return result
    
    def classify_products_abc(self) -> pd.DataFrame:
        """
        Classify products using ABC analysis based on revenue.
        
        A: Top 80% of revenue (typically ~20% of products)
        B: Next 15% of revenue
        C: Bottom 5% of revenue
        """
        product_stats = self.get_product_summary()
        
        # Sort by revenue
        product_stats = product_stats.sort_values('revenue', ascending=False)
        
        # Calculate cumulative revenue percentage
        total_revenue = product_stats['revenue'].sum()
        product_stats['cumulative_revenue'] = product_stats['revenue'].cumsum()
        product_stats['cumulative_revenue_pct'] = (
            product_stats['cumulative_revenue'] / total_revenue * 100
        )
        
        # Classify
        def classify(pct):
            if pct <= 80:
                return 'A'
            elif pct <= 95:
                return 'B'
            else:
                return 'C'
        
        product_stats['abc_class'] = product_stats['cumulative_revenue_pct'].apply(classify)
        
        return product_stats
    
    def get_fast_moving_products(self, n: int = 20) -> pd.DataFrame:
        """Identify fast-moving products based on sales velocity."""
        product_stats = self.get_product_summary()
        
        # Filter products that have been on market for at least 7 days
        product_stats = product_stats[product_stats['days_on_market'] >= 7]
        
        # Select columns based on what's available
        base_cols = ['item_code', 'item_name', 'category', 'sales_velocity', 
                     'quantity_sold', 'refund_quantity', 'net_quantity', 'revenue', 'orders', 'last_sale']
        
        # Add units_sold and pieces_sold if they exist
        display_cols = []
        for col in base_cols:
            if col == 'quantity_sold':
                if 'units_sold' in product_stats.columns:
                    display_cols.append('units_sold')
                if 'pieces_sold' in product_stats.columns:
                    display_cols.append('pieces_sold')
            display_cols.append(col)
        
        # Filter to only existing columns
        display_cols = [col for col in display_cols if col in product_stats.columns]
        
        fast_movers = product_stats.nlargest(n, 'sales_velocity')[display_cols]
        
        return fast_movers
    
    def get_slow_moving_products(self, n: int = 20) -> pd.DataFrame:
        """Identify slow-moving products based on sales velocity."""
        product_stats = self.get_product_summary()
        
        # Filter products that have been on market for at least 30 days
        product_stats = product_stats[product_stats['days_on_market'] >= 30]
        
        # Select columns based on what's available
        base_cols = ['item_code', 'item_name', 'category', 'sales_velocity',
                     'quantity_sold', 'refund_quantity', 'net_quantity', 'revenue', 'days_since_last_sale', 'last_sale']
        
        # Add units_sold and pieces_sold if they exist
        display_cols = []
        for col in base_cols:
            if col == 'quantity_sold':
                if 'units_sold' in product_stats.columns:
                    display_cols.append('units_sold')
                if 'pieces_sold' in product_stats.columns:
                    display_cols.append('pieces_sold')
            display_cols.append(col)
        
        # Filter to only existing columns
        display_cols = [col for col in display_cols if col in product_stats.columns]
        
        slow_movers = product_stats.nsmallest(n, 'sales_velocity')[display_cols]
        
        return slow_movers
    
    def get_product_lifecycle_stage(self) -> pd.DataFrame:
        """
        Classify products by lifecycle stage based on sales trends.
        
        Stages:
        - Introduction: New products (< 30 days on market)
        - Growth: Sales increasing
        - Maturity: Sales stable
        - Decline: Sales decreasing
        """
        product_stats = self.get_product_summary()
        
        # Calculate trend for each product
        product_trends = []
        
        for _, product in product_stats.iterrows():
            item_name = product['item_name']
            days_on_market = product['days_on_market']
            
            # Get time series for this product
            product_sales = self.data[self.data['item_name'] == item_name].copy()
            product_sales = product_sales.groupby('date')['quantity'].sum().reset_index()
            
            # Classify lifecycle stage
            if days_on_market < 30:
                stage = 'Introduction'
                trend = 'N/A'
            elif len(product_sales) < 10:
                stage = 'Introduction'
                trend = 'Insufficient Data'
            else:
                # Calculate trend using recent vs older data
                mid_point = len(product_sales) // 2
                older_avg = product_sales.iloc[:mid_point]['quantity'].mean()
                recent_avg = product_sales.iloc[mid_point:]['quantity'].mean()
                
                if recent_avg > older_avg * 1.2:
                    stage = 'Growth'
                    trend = 'Increasing'
                elif recent_avg < older_avg * 0.8:
                    stage = 'Decline'
                    trend = 'Decreasing'
                else:
                    stage = 'Maturity'
                    trend = 'Stable'
            
            product_trends.append({
                'item_code': product['item_code'],
                'item_name': item_name,
                'category': product['category'],
                'lifecycle_stage': stage,
                'trend': trend,
                'days_on_market': days_on_market,
                'quantity_sold': product['quantity_sold'],
                'refund_quantity': product['refund_quantity'],
                'net_quantity': product['net_quantity'],
                'revenue': product['revenue'],
                'sales_velocity': product['sales_velocity']
            })
        
        return pd.DataFrame(product_trends)
    
    def get_inventory_planning_signals(self) -> pd.DataFrame:
        """
        Generate inventory planning signals based on sales data.
        
        Signals:
        - Reorder: Fast-moving items that need restocking
        - Overstock: Slow-moving items with potential excess
        - Optimal: Well-balanced inventory
        - Monitor: Items requiring attention
        """
        product_stats = self.get_product_summary()
        
        # Calculate z-scores for velocity
        mean_velocity = product_stats['sales_velocity'].mean()
        std_velocity = product_stats['sales_velocity'].std()
        
        if std_velocity > 0:
            product_stats['velocity_zscore'] = (
                (product_stats['sales_velocity'] - mean_velocity) / std_velocity
            )
        else:
            product_stats['velocity_zscore'] = 0
        
        # Generate signals
        def generate_signal(row):
            velocity_z = row['velocity_zscore']
            days_since_sale = row['days_since_last_sale']
            
            if velocity_z > 1.5:
                return 'Reorder - High Demand'
            elif velocity_z < -1.5 and days_since_sale > 30:
                return 'Overstock - Low Demand'
            elif days_since_sale > 60:
                return 'Monitor - No Recent Sales'
            elif velocity_z > 0.5:
                return 'Reorder - Moderate Demand'
            else:
                return 'Optimal'
        
        product_stats['inventory_signal'] = product_stats.apply(generate_signal, axis=1)
        
        # Calculate recommended reorder quantity (simplified)
        # Based on average daily sales * lead time (assume 14 days)
        product_stats['recommended_reorder_qty'] = (
            product_stats['sales_velocity'] * 14
        ).round(0).astype(int)
        
        return product_stats[
            ['item_code', 'item_name', 'category', 'inventory_signal',
             'sales_velocity', 'recommended_reorder_qty', 'days_since_last_sale',
             'quantity_sold', 'refund_quantity', 'net_quantity', 'revenue']
        ].sort_values('sales_velocity', ascending=False)
    
    def get_product_demand_trends(self, item_name: str) -> pd.DataFrame:
        """Get detailed demand trends for a specific product."""
        product_data = self.data[self.data['item_name'] == item_name].copy()
        
        if len(product_data) == 0:
            return pd.DataFrame()
        
        # Daily aggregation
        daily_demand = product_data.groupby('date').agg({
            'quantity': 'sum',
            'total': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        
        daily_demand.columns = ['date', 'quantity', 'revenue', 'orders']
        
        # Calculate moving averages
        daily_demand['quantity_ma7'] = daily_demand['quantity'].rolling(window=7, min_periods=1).mean()
        daily_demand['quantity_ma30'] = daily_demand['quantity'].rolling(window=30, min_periods=1).mean()
        
        # Calculate growth rates
        daily_demand['quantity_growth'] = daily_demand['quantity'].pct_change() * 100
        
        return daily_demand
    
    def get_category_performance(self) -> pd.DataFrame:
        """Analyze performance by product category."""
        category_stats = self.data.groupby('category').agg({
            'total': 'sum',
            'quantity': 'sum',
            'order_id': 'nunique',
            'customer_name': 'nunique',
            'item_name': 'nunique'
        }).reset_index()
        
        category_stats.columns = [
            'category', 'revenue', 'quantity_sold', 'orders',
            'unique_customers', 'unique_products'
        ]
        
        # Calculate metrics
        total_revenue = category_stats['revenue'].sum()
        category_stats['revenue_pct'] = (category_stats['revenue'] / total_revenue * 100).round(2)
        category_stats['avg_order_value'] = category_stats['revenue'] / category_stats['orders']
        category_stats['avg_price'] = category_stats['revenue'] / category_stats['quantity_sold']
        
        return category_stats.sort_values('revenue', ascending=False)
    
    def get_product_seasonality(self, item_name: str) -> Dict:
        """Analyze seasonality patterns for a specific product."""
        product_data = self.data[self.data['item_name'] == item_name].copy()
        
        if len(product_data) == 0:
            return {}
        
        # Monthly patterns
        monthly = product_data.groupby('month')['quantity'].sum().to_dict()
        
        # Day of week patterns
        dow = product_data.groupby('day_of_week')['quantity'].sum().to_dict()
        
        return {
            'monthly_patterns': monthly,
            'day_of_week_patterns': dow,
            'total_quantity': product_data['quantity'].sum(),
            'date_range': (product_data['date'].min(), product_data['date'].max())
        }
    
    def get_price_sensitivity_analysis(self) -> pd.DataFrame:
        """Analyze relationship between price and sales volume."""
        # Group by product and calculate price bands
        product_price_analysis = []
        
        for item_name in self.data['item_name'].unique():
            product_data = self.data[self.data['item_name'] == item_name].copy()
            
            if len(product_data) < 10:  # Skip products with insufficient data
                continue
            
            # Calculate price statistics
            avg_price = product_data['selling_price'].mean()
            price_std = product_data['selling_price'].std()
            
            if price_std == 0:
                continue
            
            # Categorize sales by price level
            product_data['price_category'] = pd.cut(
                product_data['selling_price'],
                bins=[0, avg_price - price_std, avg_price + price_std, np.inf],
                labels=['Low', 'Medium', 'High']
            )
            
            # Compare sales by price category
            price_impact = product_data.groupby('price_category')['quantity'].sum().to_dict()
            
            product_price_analysis.append({
                'item_name': item_name,
                'avg_price': avg_price,
                'price_std': price_std,
                'low_price_sales': price_impact.get('Low', 0),
                'medium_price_sales': price_impact.get('Medium', 0),
                'high_price_sales': price_impact.get('High', 0),
                'total_sales': product_data['quantity'].sum()
            })
        
        return pd.DataFrame(product_price_analysis)
    
    def get_product_penetration(self) -> pd.DataFrame:
        """Calculate customer penetration rate for each product."""
        # Use only sales data (exclude refunds) for penetration
        sales_data = self.data[~self.data['is_refund']]
        total_customers = sales_data['customer_name'].nunique()
        
        product_penetration = sales_data.groupby(['item_code', 'item_name', 'category']).agg({
            'customer_name': 'nunique',
            'total': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        product_penetration.columns = [
            'item_code', 'item_name', 'category', 'unique_customers', 'revenue', 'quantity_sold'
        ]
        
        # Calculate penetration rate
        product_penetration['penetration_rate_pct'] = (
            product_penetration['unique_customers'] / total_customers * 100
        ).round(2)
        
        return product_penetration.sort_values('penetration_rate_pct', ascending=False)
    
    def get_high_refund_products(self, min_sales: int = 10, min_refund_rate: float = 5.0) -> pd.DataFrame:
        """
        Identify products with high refund rates.
        
        Args:
            min_sales: Minimum number of sales orders to consider
            min_refund_rate: Minimum refund rate percentage to flag
        
        Returns:
            DataFrame with products sorted by refund rate
        """
        product_stats = self.get_product_summary()
        
        # Filter products with sufficient sales and high refund rates
        high_refund = product_stats[
            (product_stats['orders'] >= min_sales) &
            (product_stats['refund_rate_pct'] >= min_refund_rate)
        ].copy()
        
        # Sort by refund rate
        high_refund = high_refund.sort_values('refund_rate_pct', ascending=False)
        
        return high_refund[
            ['item_code', 'item_name', 'category', 'orders', 'refund_orders',
             'gross_revenue', 'refund_amount', 'revenue', 'refund_rate_pct',
             'quantity_sold', 'refund_quantity']
        ]

