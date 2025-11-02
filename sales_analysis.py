"""Sales analysis module for revenue tracking, trends, and anomaly detection."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, List, Optional
from scipy import stats
from sklearn.ensemble import IsolationForest


class SalesAnalyzer:
    """Analyzes sales data for trends, patterns, and anomalies."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize sales analyzer.
        
        Args:
            data: Preprocessed sales DataFrame
        """
        self.data = data
        # Caches for expensive computations
        self._daily_trends_cache: Optional[pd.DataFrame] = None
        self._weekly_trends_cache: Optional[pd.DataFrame] = None
        self._monthly_trends_cache: Optional[pd.DataFrame] = None
        
    def get_overall_metrics(self) -> Dict:
        """Calculate overall sales metrics."""
        df = self.data
        
        total_revenue = df['total'].sum()
        total_orders = df['order_id'].nunique()
        total_items_sold = df['quantity'].sum()
        unique_customers = df['customer_name'].nunique()
        
        # Average order value
        order_totals = df.groupby('order_id')['total'].sum()
        avg_order_value = order_totals.mean()
        
        # Average items per order
        items_per_order = df.groupby('order_id')['quantity'].sum()
        avg_items_per_order = items_per_order.mean()
        
        # Date range
        date_range_days = (df['date'].max() - df['date'].min()).days
        
        # Daily average revenue
        daily_revenue = total_revenue / max(date_range_days, 1)
        
        return {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'unique_orders': total_orders,  # Alias for dashboard compatibility
            'total_items_sold': total_items_sold,
            'unique_customers': unique_customers,
            'avg_order_value': avg_order_value,
            'avg_items_per_order': avg_items_per_order,
            'date_range_days': date_range_days,
            'daily_avg_revenue': daily_revenue,
            'start_date': df['date'].min(),
            'end_date': df['date'].max()
        }
    
    def get_daily_trends(self) -> pd.DataFrame:
        """Calculate daily sales trends. (CACHED)"""
        if self._daily_trends_cache is not None:
            return self._daily_trends_cache
        
        daily = self.data.groupby('date').agg({
            'total': 'sum',
            'order_id': 'nunique',
            'customer_name': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        
        daily.columns = ['date', 'revenue', 'orders', 'customers', 'items_sold']
        
        # Calculate moving averages
        daily['revenue_ma7'] = daily['revenue'].rolling(window=7, min_periods=1).mean()
        daily['revenue_ma30'] = daily['revenue'].rolling(window=30, min_periods=1).mean()
        
        # Calculate growth rates
        daily['revenue_growth'] = daily['revenue'].pct_change() * 100
        
        self._daily_trends_cache = daily
        return daily
    
    def get_weekly_trends(self) -> pd.DataFrame:
        """Calculate weekly sales trends. (CACHED)"""
        if self._weekly_trends_cache is not None:
            return self._weekly_trends_cache
        
        df = self.data.copy()
        df['year_week'] = df['date'].dt.strftime('%Y-W%U')
        
        weekly = df.groupby('year_week').agg({
            'total': 'sum',
            'order_id': 'nunique',
            'customer_name': 'nunique',
            'quantity': 'sum',
            'date': 'min'
        }).reset_index()
        
        weekly.columns = ['year_week', 'revenue', 'orders', 'customers', 'items_sold', 'week_start']
        weekly = weekly.sort_values('week_start')
        
        # Calculate growth
        weekly['revenue_growth'] = weekly['revenue'].pct_change() * 100
        
        self._weekly_trends_cache = weekly
        return weekly
    
    def get_monthly_trends(self) -> pd.DataFrame:
        """Calculate monthly sales trends. (CACHED)"""
        if self._monthly_trends_cache is not None:
            return self._monthly_trends_cache
        
        df = self.data.copy()
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        
        monthly = df.groupby('year_month').agg({
            'total': 'sum',
            'order_id': 'nunique',
            'customer_name': 'nunique',
            'quantity': 'sum',
            'date': 'min'
        }).reset_index()
        
        monthly.columns = ['year_month', 'revenue', 'orders', 'customers', 'items_sold', 'month_start']
        monthly = monthly.sort_values('month_start')
        
        # Calculate growth
        monthly['revenue_growth'] = monthly['revenue'].pct_change() * 100
        monthly['mom_growth'] = monthly['revenue'].pct_change() * 100  # Month-over-month
        
        self._monthly_trends_cache = monthly
        return monthly
    
    def get_top_products(self, n: int = 10, metric: str = 'revenue') -> pd.DataFrame:
        """
        Get top products by specified metric.
        
        Args:
            n: Number of top products to return
            metric: 'revenue', 'quantity', or 'orders'
        """
        if metric == 'revenue':
            top = self.data.groupby(['item_code', 'item_name']).agg({
                'total': 'sum',
                'quantity': 'sum',
                'order_id': 'nunique'
            }).reset_index()
            top.columns = ['item_code', 'item_name', 'revenue', 'quantity', 'orders']
            top = top.sort_values('revenue', ascending=False).head(n)
            
        elif metric == 'quantity':
            top = self.data.groupby(['item_code', 'item_name']).agg({
                'quantity': 'sum',
                'total': 'sum',
                'order_id': 'nunique'
            }).reset_index()
            top.columns = ['item_code', 'item_name', 'quantity', 'revenue', 'orders']
            top = top.sort_values('quantity', ascending=False).head(n)
            
        elif metric == 'orders':
            top = self.data.groupby(['item_code', 'item_name']).agg({
                'order_id': 'nunique',
                'total': 'sum',
                'quantity': 'sum'
            }).reset_index()
            top.columns = ['item_code', 'item_name', 'orders', 'revenue', 'quantity']
            top = top.sort_values('orders', ascending=False).head(n)
        
        return top
    
    def get_top_categories(self, n: int = 10) -> pd.DataFrame:
        """Get top product categories by revenue."""
        top_cat = self.data.groupby('category').agg({
            'total': 'sum',
            'quantity': 'sum',
            'order_id': 'nunique',
            'item_name': 'nunique'
        }).reset_index()
        
        top_cat.columns = ['category', 'revenue', 'quantity', 'orders', 'unique_products']
        top_cat = top_cat.sort_values('revenue', ascending=False).head(n)
        
        # Calculate percentage of total
        total_revenue = self.data['total'].sum()
        top_cat['revenue_pct'] = (top_cat['revenue'] / total_revenue * 100).round(2)
        
        return top_cat
    
    def get_hourly_patterns(self) -> pd.DataFrame:
        """Analyze sales patterns by hour of day."""
        df = self.data.copy()
        
        # Try multiple approaches to extract hour
        df['hour'] = None
        
        # Approach 1: Try datetime column first (most reliable)
        if 'datetime' in df.columns:
            try:
                datetime_hours = pd.to_datetime(df['datetime'], errors='coerce').dt.hour
                if datetime_hours.notna().any():
                    df['hour'] = datetime_hours
            except:
                pass
        
        # Approach 2: If hour is still None, try time column
        if df['hour'].isna().all() and 'time' in df.columns:
            try:
                # Check if any row has a time object with hour attribute
                has_time_object = False
                for val in df['time'].head(10):
                    if pd.notna(val) and hasattr(val, 'hour'):
                        has_time_object = True
                        break
                
                if has_time_object:
                    # It's a time object, extract hour directly
                    df['hour'] = df['time'].apply(lambda x: x.hour if pd.notna(x) and hasattr(x, 'hour') else None)
                else:
                    # Try parsing as string
                    df['hour'] = pd.to_datetime(df['time'].astype(str), format='%H:%M:%S', errors='coerce').dt.hour
                    
                # If still no valid hours, try one more approach
                if df['hour'].isna().all():
                    df['hour'] = pd.to_datetime(df['time'], errors='coerce').dt.hour
            except Exception as e:
                # Last resort: try to convert to datetime and extract hour
                try:
                    df['hour'] = pd.to_datetime(df['time'], errors='coerce').dt.hour
                except:
                    pass
        
        # Approach 3: If still no hour, try extracting from date column
        if df['hour'].isna().all() and 'date' in df.columns:
            try:
                date_hours = pd.to_datetime(df['date'], errors='coerce').dt.hour
                # Only use if date has meaningful time info (not all zeros)
                if (date_hours != 0).any():
                    df['hour'] = date_hours
            except:
                pass
        
        # Final fallback: if no time data found, set all to 0
        if df['hour'].isna().all():
            df['hour'] = 0
        
        # Remove NaN hours and convert to int
        df = df.dropna(subset=['hour'])
        df['hour'] = df['hour'].astype(int)
        
        # Group by hour
        hourly = df.groupby('hour').agg({
            'total': 'sum',
            'order_id': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        
        hourly.columns = ['hour', 'revenue', 'orders', 'items_sold']
        
        # Create a complete hour range (0-23) and merge with actual data
        all_hours = pd.DataFrame({'hour': range(24)})
        hourly = all_hours.merge(hourly, on='hour', how='left')
        
        # Fill missing values with 0
        hourly['revenue'] = hourly['revenue'].fillna(0)
        hourly['orders'] = hourly['orders'].fillna(0)
        hourly['items_sold'] = hourly['items_sold'].fillna(0)
        
        # Calculate percentage of daily total
        total_revenue = hourly['revenue'].sum()
        if total_revenue > 0:
            hourly['revenue_pct'] = (hourly['revenue'] / total_revenue * 100).round(2)
        else:
            hourly['revenue_pct'] = 0
        
        return hourly
    
    def get_day_of_week_patterns(self) -> pd.DataFrame:
        """Analyze sales patterns by day of week."""
        dow = self.data.groupby('day_name').agg({
            'total': 'sum',
            'order_id': 'nunique',
            'customer_name': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        
        dow.columns = ['day', 'revenue', 'orders', 'customers', 'items_sold']
        
        # Order days properly
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow['day'] = pd.Categorical(dow['day'], categories=day_order, ordered=True)
        dow = dow.sort_values('day')
        
        # Calculate averages
        total_weeks = (self.data['date'].max() - self.data['date'].min()).days / 7
        if total_weeks > 0:
            dow['avg_revenue'] = dow['revenue'] / total_weeks
            dow['avg_orders'] = dow['orders'] / total_weeks
        
        return dow
    
    def detect_anomalies(self, contamination: float = 0.05) -> pd.DataFrame:
        """
        Detect anomalies in daily sales using Isolation Forest.
        
        Args:
            contamination: Expected proportion of outliers (0.05 = 5%)
        """
        # Get daily aggregates
        daily = self.data.groupby('date').agg({
            'total': 'sum',
            'order_id': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        
        # Prepare features for anomaly detection
        features = daily[['total', 'order_id', 'quantity']].values
        
        # Normalize features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Detect anomalies
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        daily['anomaly'] = iso_forest.fit_predict(features_scaled)
        daily['anomaly_score'] = iso_forest.score_samples(features_scaled)
        
        # Convert anomaly labels (-1 for anomaly, 1 for normal)
        daily['is_anomaly'] = daily['anomaly'] == -1
        
        # Calculate z-scores for interpretation
        daily['revenue_zscore'] = stats.zscore(daily['total'])
        daily['orders_zscore'] = stats.zscore(daily['order_id'])
        
        return daily.sort_values('date')
    
    def get_seasonal_patterns(self) -> Dict:
        """Analyze seasonal patterns in sales."""
        df = self.data.copy()
        
        # Monthly seasonality
        monthly_avg = df.groupby('month')['total'].mean().to_dict()
        
        # Day of week seasonality
        dow_avg = df.groupby('day_of_week')['total'].mean().to_dict()
        
        # Quarter analysis
        df['quarter'] = df['date'].dt.quarter
        quarterly = df.groupby('quarter').agg({
            'total': ['sum', 'mean'],
            'order_id': 'nunique'
        }).reset_index()
        
        return {
            'monthly_averages': monthly_avg,
            'day_of_week_averages': dow_avg,
            'quarterly_summary': quarterly
        }
    
    def get_growth_analysis(self) -> Dict:
        """Calculate various growth metrics."""
        df = self.data.copy()
        
        # Sort by date
        df = df.sort_values('date')
        
        # Split into first and second half
        mid_date = df['date'].min() + (df['date'].max() - df['date'].min()) / 2
        first_half = df[df['date'] <= mid_date]
        second_half = df[df['date'] > mid_date]
        
        # Calculate metrics for each half
        first_half_revenue = first_half['total'].sum()
        second_half_revenue = second_half['total'].sum()
        
        first_half_orders = first_half['order_id'].nunique()
        second_half_orders = second_half['order_id'].nunique()
        
        # Calculate growth rates
        revenue_growth = ((second_half_revenue - first_half_revenue) / first_half_revenue * 100) if first_half_revenue > 0 else 0
        orders_growth = ((second_half_orders - first_half_orders) / first_half_orders * 100) if first_half_orders > 0 else 0
        
        return {
            'first_half_revenue': first_half_revenue,
            'second_half_revenue': second_half_revenue,
            'revenue_growth_pct': revenue_growth,
            'first_half_orders': first_half_orders,
            'second_half_orders': second_half_orders,
            'orders_growth_pct': orders_growth,
            'mid_date': mid_date
        }
    
    def get_sales_velocity(self) -> pd.DataFrame:
        """Calculate sales velocity (revenue per day) trends."""
        daily = self.get_daily_trends()
        
        # Calculate rolling velocity
        daily['velocity_7d'] = daily['revenue'].rolling(window=7, min_periods=1).mean()
        daily['velocity_30d'] = daily['revenue'].rolling(window=30, min_periods=1).mean()
        
        # Calculate acceleration (change in velocity)
        daily['acceleration'] = daily['velocity_7d'].diff()
        
        return daily

