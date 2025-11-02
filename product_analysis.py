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
        self.data = data
        self.current_date = data['date'].max()
        # Cache for expensive computations
        self._product_summary_cache: Optional[pd.DataFrame] = None
        
    def get_product_summary(self) -> pd.DataFrame:
        """Get comprehensive summary for each product. (CACHED)"""
        # Return cached result if available
        if self._product_summary_cache is not None:
            return self._product_summary_cache
        
        product_stats = self.data.groupby(['item_code', 'item_name', 'category']).agg({
            'order_id': 'nunique',
            'quantity': 'sum',
            'total': 'sum',
            'customer_name': 'nunique',
            'date': ['min', 'max']
        }).reset_index()
        
        # Flatten column names
        product_stats.columns = [
            'item_code', 'item_name', 'category', 'orders', 'quantity_sold',
            'revenue', 'unique_customers', 'first_sale', 'last_sale'
        ]
        
        # Calculate metrics
        product_stats['avg_price'] = product_stats['revenue'] / product_stats['quantity_sold']
        product_stats['avg_quantity_per_order'] = product_stats['quantity_sold'] / product_stats['orders']
        
        # Days on market
        product_stats['days_on_market'] = (
            product_stats['last_sale'] - product_stats['first_sale']
        ).dt.days + 1
        
        # Days since last sale
        product_stats['days_since_last_sale'] = (
            self.current_date - product_stats['last_sale']
        ).dt.days
        
        # Sales velocity (units per day)
        product_stats['sales_velocity'] = (
            product_stats['quantity_sold'] / product_stats['days_on_market']
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
        
        fast_movers = product_stats.nlargest(n, 'sales_velocity')[
            ['item_code', 'item_name', 'category', 'sales_velocity', 
             'quantity_sold', 'revenue', 'orders', 'last_sale']
        ]
        
        return fast_movers
    
    def get_slow_moving_products(self, n: int = 20) -> pd.DataFrame:
        """Identify slow-moving products based on sales velocity."""
        product_stats = self.get_product_summary()
        
        # Filter products that have been on market for at least 30 days
        product_stats = product_stats[product_stats['days_on_market'] >= 30]
        
        slow_movers = product_stats.nsmallest(n, 'sales_velocity')[
            ['item_code', 'item_name', 'category', 'sales_velocity',
             'quantity_sold', 'revenue', 'days_since_last_sale', 'last_sale']
        ]
        
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
             'quantity_sold', 'revenue']
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
        total_customers = self.data['customer_name'].nunique()
        
        product_penetration = self.data.groupby(['item_code', 'item_name', 'category']).agg({
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

