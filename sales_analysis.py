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
        
        # Verify order_id source
        self._verify_order_id_source()
        
    def _verify_order_id_source(self) -> None:
        """Verify the source of order_id and display information."""
        if 'order_id' not in self.data.columns:
            print("⚠ WARNING: No order_id column found in data!")
            return
        
        # Check order_id characteristics
        unique_orders = self.data['order_id'].nunique()
        total_records = len(self.data)
        
        # Check if order_ids look like receipt numbers (typically larger values)
        # or computed IDs (sequential starting from 0)
        min_order_id = self.data['order_id'].min()
        max_order_id = self.data['order_id'].max()
        
        # Heuristic: If order_ids are small and sequential, likely computed
        # If order_ids are large or non-sequential, likely from Receipt column
        if max_order_id < total_records and min_order_id >= -1:
            order_source = "Computed (time-based grouping)"
            print(f"ℹ️ Sales Analysis: Using COMPUTED order_id (sequential: {min_order_id} to {max_order_id})")
            print(f"   → Orders grouped by customer + time window (30 min)")
        else:
            order_source = "Receipt column"
            print(f"ℹ️ Sales Analysis: Using RECEIPT-based order_id (range: {min_order_id} to {max_order_id})")
            print(f"   → Orders grouped by actual Receipt numbers")
        
        print(f"   → Total: {unique_orders:,} unique orders from {total_records:,} transactions")
        
        # Store for later reference
        self.order_id_source = order_source
        self.order_id_range = (min_order_id, max_order_id)
        self.unique_order_count = unique_orders
    
    def get_overall_metrics(self) -> Dict:
        """Calculate overall sales metrics with refund handling."""
        df = self.data
        
        # Separate refunds from regular sales
        sales_df = df[~df['is_refund']]
        refunds_df = df[df['is_refund']]
        
        # Revenue metrics
        gross_revenue = sales_df['total'].sum()
        refund_amount = abs(refunds_df['total'].sum())
        net_revenue = df['total'].sum()  # Already includes negative refunds
        
        # Order and customer metrics
        total_orders = df['order_id'].nunique()
        total_sales_orders = sales_df['order_id'].nunique()
        total_refund_orders = refunds_df['order_id'].nunique()
        unique_customers = df['customer_name'].nunique()
        
        # Item metrics
        total_items_sold = sales_df['quantity'].sum()
        total_items_refunded = abs(refunds_df['quantity'].sum())
        net_items = df['quantity'].sum()
        
        # Average order value
        order_totals = df.groupby('order_id')['total'].sum()
        avg_order_value = order_totals.mean()
        
        # Average items per order (only counting sales)
        if total_sales_orders > 0:
            avg_items_per_order = total_items_sold / total_sales_orders
        else:
            avg_items_per_order = 0
        
        # Date range
        date_range_days = (df['date'].max() - df['date'].min()).days
        
        # Daily average revenue (using net revenue)
        daily_revenue = net_revenue / max(date_range_days, 1)
        
        # Refund metrics
        refund_rate = (refund_amount / gross_revenue * 100) if gross_revenue > 0 else 0
        refund_transaction_rate = (len(refunds_df) / len(df) * 100) if len(df) > 0 else 0
        
        return {
            'gross_revenue': gross_revenue,
            'refund_amount': refund_amount,
            'net_revenue': net_revenue,
            'total_revenue': net_revenue,  # Alias for backward compatibility
            'refund_rate_pct': refund_rate,
            'total_orders': total_orders,
            'unique_orders': total_orders,  # Alias for dashboard compatibility
            'sales_orders': total_sales_orders,
            'refund_orders': total_refund_orders,
            'total_items_sold': total_items_sold,
            'total_items_refunded': total_items_refunded,
            'net_items_sold': net_items,
            'unique_customers': unique_customers,
            'avg_order_value': avg_order_value,
            'avg_items_per_order': avg_items_per_order,
            'date_range_days': date_range_days,
            'daily_avg_revenue': daily_revenue,
            'start_date': df['date'].min(),
            'end_date': df['date'].max(),
            'num_refund_transactions': len(refunds_df),
            'num_sales_transactions': len(sales_df),
            'refund_transaction_rate_pct': refund_transaction_rate
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
        
        Shows Units, Pieces, and Quantity for each product:
        - Units: Full units/boxes sold (integer)
        - Pieces: Loose pieces sold (integer)
        - Quantity: Total effective quantity sold (can be fractional) ⭐
        - Price Per Unit: Average price per unit sold
        
        Args:
            n: Number of top products to return
            metric: 'revenue', 'quantity', or 'orders'
        """
        # Filter out refunds for top products analysis
        sales_data = self.data[~self.data['is_refund']].copy()
        
        # Determine which columns are available
        agg_dict = {
            'total': 'sum',
            'quantity': 'sum',
            'order_id': 'nunique'
        }
        
        # Add units and pieces if they exist
        if 'units' in sales_data.columns:
            agg_dict['units'] = 'sum'
        if 'pieces' in sales_data.columns:
            agg_dict['pieces'] = 'sum'
        
        # Aggregate data
        top = sales_data.groupby(['item_code', 'item_name']).agg(agg_dict).reset_index()
        
        # Rename columns using dictionary (safer than list assignment)
        rename_dict = {
            'total': 'revenue',
            'order_id': 'orders'
        }
        top = top.rename(columns=rename_dict)
        
        # Calculate price per unit (revenue / quantity)
        top['price_per_unit'] = top['revenue'] / top['quantity'].replace(0, np.nan)
        top['price_per_unit'] = top['price_per_unit'].fillna(0).round(2)
        
        # Sort based on metric
        if metric == 'revenue':
            top = top.sort_values('revenue', ascending=False).head(n)
            # Reorder columns for display
            col_order = ['item_code', 'item_name', 'revenue']
            if 'units' in top.columns:
                col_order.append('units')
            if 'pieces' in top.columns:
                col_order.append('pieces')
            col_order.extend(['quantity', 'price_per_unit', 'orders'])
            top = top[[col for col in col_order if col in top.columns]]
            
        elif metric == 'quantity':
            top = top.sort_values('quantity', ascending=False).head(n)
            # Reorder columns for display
            col_order = ['item_code', 'item_name']
            if 'units' in top.columns:
                col_order.append('units')
            if 'pieces' in top.columns:
                col_order.append('pieces')
            col_order.extend(['quantity', 'revenue', 'price_per_unit', 'orders'])
            top = top[[col for col in col_order if col in top.columns]]
            
        elif metric == 'orders':
            top = top.sort_values('orders', ascending=False).head(n)
            # Reorder columns for display
            col_order = ['item_code', 'item_name', 'orders']
            if 'units' in top.columns:
                col_order.append('units')
            if 'pieces' in top.columns:
                col_order.append('pieces')
            col_order.extend(['quantity', 'revenue', 'price_per_unit'])
            top = top[[col for col in col_order if col in top.columns]]
        
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
            
        Returns:
            DataFrame with daily aggregates and anomaly flags.
            Note: 'num_orders' column contains COUNT of unique orders per day,
                  not the actual order_id values.
        """
        # Get daily aggregates
        daily = self.data.groupby('date').agg({
            'total': 'sum',
            'order_id': 'nunique',  # Count of unique orders
            'quantity': 'sum'
        }).reset_index()
        
        # Rename order_id to num_orders to avoid confusion
        # (it contains COUNT of orders, not actual order_id values)
        daily.rename(columns={'order_id': 'num_orders'}, inplace=True)
        
        # Prepare features for anomaly detection
        features = daily[['total', 'num_orders', 'quantity']].values
        
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
        daily['orders_zscore'] = stats.zscore(daily['num_orders'])
        
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
    
    def verify_order_id_usage(self) -> Dict:
        """
        Verify order_id source and provide detailed information.
        
        Returns:
            Dictionary with order_id verification details including:
            - Source (Receipt vs Computed)
            - Range of order_id values
            - Sample orders with their items
            - Statistics
        """
        if 'order_id' not in self.data.columns:
            return {
                'error': 'No order_id column found',
                'has_order_id': False
            }
        
        # Get order_id statistics
        unique_orders = self.data['order_id'].nunique()
        total_transactions = len(self.data)
        min_id = self.data['order_id'].min()
        max_id = self.data['order_id'].max()
        
        # Determine source
        if max_id < total_transactions and min_id >= -1:
            source = "Computed (time-based)"
            method = "Customer + Time Window (30 min)"
        else:
            source = "Receipt column"
            method = "Actual Receipt numbers from data"
        
        # Get order size distribution
        items_per_order = self.data.groupby('order_id').size()
        
        # Sample orders
        sample_order_ids = self.data['order_id'].unique()[:5]
        sample_orders = []
        for order_id in sample_order_ids:
            order_data = self.data[self.data['order_id'] == order_id]
            sample_orders.append({
                'order_id': int(order_id) if isinstance(order_id, (int, np.integer)) else str(order_id),
                'items': order_data['item_name'].tolist(),
                'customer': order_data['customer_name'].iloc[0],
                'date': order_data['date'].iloc[0],
                'total': float(order_data['total'].sum()),
                'num_items': len(order_data)
            })
        
        return {
            'has_order_id': True,
            'source': source,
            'grouping_method': method,
            'unique_orders': int(unique_orders),
            'total_transactions': int(total_transactions),
            'avg_items_per_order': float(items_per_order.mean()),
            'min_order_id': int(min_id) if isinstance(min_id, (int, np.integer)) else str(min_id),
            'max_order_id': int(max_id) if isinstance(max_id, (int, np.integer)) else str(max_id),
            'single_item_orders': int((items_per_order == 1).sum()),
            'multi_item_orders': int((items_per_order > 1).sum()),
            'multi_item_percentage': float((items_per_order > 1).sum() / len(items_per_order) * 100),
            'sample_orders': sample_orders
        }
    
    def print_order_id_verification(self) -> None:
        """Print human-readable order_id verification information."""
        info = self.verify_order_id_usage()
        
        if not info.get('has_order_id'):
            print("\n⚠ ERROR: No order_id column found in data!")
            return
        
        print("\n" + "="*70)
        print("ORDER ID VERIFICATION - SALES ANALYSIS")
        print("="*70)
        
        print(f"\n🔍 Order ID Source: {info['source']}")
        print(f"   Grouping Method: {info['grouping_method']}")
        
        print(f"\n📊 Statistics:")
        print(f"   • Total Transactions: {info['total_transactions']:,}")
        print(f"   • Unique Orders: {info['unique_orders']:,}")
        print(f"   • Order ID Range: {info['min_order_id']} to {info['max_order_id']}")
        print(f"   • Avg Items per Order: {info['avg_items_per_order']:.2f}")
        
        print(f"\n📦 Order Distribution:")
        print(f"   • Single-Item Orders: {info['single_item_orders']:,} ({100-info['multi_item_percentage']:.1f}%)")
        print(f"   • Multi-Item Orders: {info['multi_item_orders']:,} ({info['multi_item_percentage']:.1f}%)")
        
        print(f"\n🔍 Sample Orders (First 5):")
        for i, order in enumerate(info['sample_orders'], 1):
            print(f"\n   Order #{order['order_id']}:")
            print(f"      Customer: {order['customer']}")
            print(f"      Date: {order['date']}")
            print(f"      Items ({order['num_items']}):")
            for item in order['items']:
                print(f"         - {item}")
            print(f"      Total: ${order['total']:.2f}")
        
        print("\n" + "="*70)
        
        # Warning if using computed IDs
        if info['source'] == "Computed (time-based)":
            print("\n⚠ WARNING: Using COMPUTED order IDs (not from Receipt column)")
            print("   • Orders are grouped by: Customer + Time Window (30 min)")
            print("   • This may not match actual receipts")
            print("   • For accurate analysis, ensure Receipt column exists in data")
        else:
            print("\n✅ Using RECEIPT-based order IDs (accurate grouping)")
        
        print("="*70 + "\n")
    
    def get_refund_analysis(self) -> Dict:
        """
        Analyze refund patterns and trends.
        
        Returns detailed refund metrics and insights.
        """
        df = self.data
        sales_df = df[~df['is_refund']]
        refunds_df = df[df['is_refund']]
        
        if len(refunds_df) == 0:
            return {
                'has_refunds': False,
                'message': 'No refunds found in the data'
            }
        
        # Overall refund metrics
        gross_revenue = sales_df['total'].sum()
        refund_amount = abs(refunds_df['total'].sum())
        refund_rate = (refund_amount / gross_revenue * 100) if gross_revenue > 0 else 0
        
        # Refund by time period
        refunds_by_month = refunds_df.groupby(refunds_df['date'].dt.to_period('M')).agg({
            'total': lambda x: abs(x.sum()),
            'order_id': 'nunique'
        }).reset_index()
        refunds_by_month.columns = ['month', 'refund_amount', 'refund_orders']
        
        # Top refunded products
        top_refunded_products = refunds_df.groupby('item_name').agg({
            'total': lambda x: abs(x.sum()),
            'quantity': lambda x: abs(x.sum()),
            'order_id': 'nunique'
        }).reset_index()
        top_refunded_products.columns = ['item_name', 'refund_amount', 'refund_quantity', 'refund_orders']
        top_refunded_products = top_refunded_products.sort_values('refund_amount', ascending=False)
        
        # Customers with most refunds
        top_refund_customers = refunds_df.groupby('customer_name').agg({
            'total': lambda x: abs(x.sum()),
            'order_id': 'nunique'
        }).reset_index()
        top_refund_customers.columns = ['customer_name', 'refund_amount', 'refund_orders']
        top_refund_customers = top_refund_customers.sort_values('refund_amount', ascending=False)
        
        # Refund trends (daily)
        daily_refunds = refunds_df.groupby('date').agg({
            'total': lambda x: abs(x.sum()),
            'order_id': 'nunique'
        }).reset_index()
        daily_refunds.columns = ['date', 'refund_amount', 'refund_orders']
        
        # Average refund value
        avg_refund_value = refund_amount / len(refunds_df) if len(refunds_df) > 0 else 0
        
        return {
            'has_refunds': True,
            'total_refund_amount': refund_amount,
            'total_refund_transactions': len(refunds_df),
            'refund_rate_pct': refund_rate,
            'avg_refund_value': avg_refund_value,
            'refunds_by_month': refunds_by_month,
            'top_refunded_products': top_refunded_products,
            'top_refund_customers': top_refund_customers,
            'daily_refunds': daily_refunds,
            'refund_orders': refunds_df['order_id'].nunique(),
            'unique_customers_with_refunds': refunds_df['customer_name'].nunique()
        }
    
    def get_monthly_category_breakdown(self) -> pd.DataFrame:
        """
        Get monthly sales breakdown by category.
        
        Returns DataFrame with columns:
        - year_month: Month in YYYY-MM format
        - month_name: Human-readable month name
        - category: Product category
        - revenue: Total revenue for that category in that month
        - quantity: Total quantity sold
        - orders: Number of unique orders
        - avg_order_value: Average order value
        """
        # Exclude refunds
        df = self.data[~self.data['is_refund']].copy()
        
        # Add month columns
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        df['month_name'] = df['date'].dt.strftime('%B %Y')
        df['month_start'] = df['date'].dt.to_period('M').dt.to_timestamp()
        
        # Group by month and category
        monthly_category = df.groupby(['year_month', 'month_name', 'month_start', 'category']).agg({
            'total': 'sum',
            'quantity': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        
        monthly_category.columns = ['year_month', 'month_name', 'month_start', 'category', 
                                    'revenue', 'quantity', 'orders']
        
        # Calculate average order value
        monthly_category['avg_order_value'] = (
            monthly_category['revenue'] / monthly_category['orders']
        ).round(2)
        
        # Sort by month and revenue
        monthly_category = monthly_category.sort_values(['month_start', 'revenue'], ascending=[True, False])
        
        return monthly_category
    
    def get_month_comparison(self, month1: str, month2: str) -> Dict:
        """
        Compare two months side by side.
        
        Args:
            month1: First month in YYYY-MM format (e.g., '2024-01')
            month2: Second month in YYYY-MM format (e.g., '2024-02')
            
        Returns:
            Dictionary with comparison metrics including:
            - Overall metrics for each month
            - Category breakdown for each month
            - Growth rates and changes
        """
        # Exclude refunds
        df = self.data[~self.data['is_refund']].copy()
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        
        # Filter data for each month
        month1_data = df[df['year_month'] == month1]
        month2_data = df[df['year_month'] == month2]
        
        if len(month1_data) == 0 or len(month2_data) == 0:
            return {
                'error': f'No data found for one or both months',
                'month1': month1,
                'month2': month2,
                'month1_records': len(month1_data),
                'month2_records': len(month2_data)
            }
        
        # Overall metrics for month 1
        month1_metrics = {
            'month': month1,
            'revenue': month1_data['total'].sum(),
            'quantity': month1_data['quantity'].sum(),
            'orders': month1_data['order_id'].nunique(),
            'customers': month1_data['customer_name'].nunique(),
            'avg_order_value': month1_data.groupby('order_id')['total'].sum().mean()
        }
        
        # Overall metrics for month 2
        month2_metrics = {
            'month': month2,
            'revenue': month2_data['total'].sum(),
            'quantity': month2_data['quantity'].sum(),
            'orders': month2_data['order_id'].nunique(),
            'customers': month2_data['customer_name'].nunique(),
            'avg_order_value': month2_data.groupby('order_id')['total'].sum().mean()
        }
        
        # Calculate changes
        changes = {
            'revenue_change': month2_metrics['revenue'] - month1_metrics['revenue'],
            'revenue_change_pct': ((month2_metrics['revenue'] - month1_metrics['revenue']) / 
                                  month1_metrics['revenue'] * 100) if month1_metrics['revenue'] > 0 else 0,
            'quantity_change': month2_metrics['quantity'] - month1_metrics['quantity'],
            'quantity_change_pct': ((month2_metrics['quantity'] - month1_metrics['quantity']) / 
                                   month1_metrics['quantity'] * 100) if month1_metrics['quantity'] > 0 else 0,
            'orders_change': month2_metrics['orders'] - month1_metrics['orders'],
            'orders_change_pct': ((month2_metrics['orders'] - month1_metrics['orders']) / 
                                 month1_metrics['orders'] * 100) if month1_metrics['orders'] > 0 else 0,
            'customers_change': month2_metrics['customers'] - month1_metrics['customers'],
            'customers_change_pct': ((month2_metrics['customers'] - month1_metrics['customers']) / 
                                    month1_metrics['customers'] * 100) if month1_metrics['customers'] > 0 else 0
        }
        
        # Category breakdown for month 1
        month1_categories = month1_data.groupby('category').agg({
            'total': 'sum',
            'quantity': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        month1_categories.columns = ['category', 'revenue', 'quantity', 'orders']
        month1_categories = month1_categories.sort_values('revenue', ascending=False)
        
        # Category breakdown for month 2
        month2_categories = month2_data.groupby('category').agg({
            'total': 'sum',
            'quantity': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        month2_categories.columns = ['category', 'revenue', 'quantity', 'orders']
        month2_categories = month2_categories.sort_values('revenue', ascending=False)
        
        # Category comparison
        category_comparison = month1_categories.merge(
            month2_categories, 
            on='category', 
            how='outer', 
            suffixes=('_m1', '_m2')
        ).fillna(0)
        
        # Calculate category changes
        category_comparison['revenue_change'] = (
            category_comparison['revenue_m2'] - category_comparison['revenue_m1']
        )
        category_comparison['revenue_change_pct'] = (
            (category_comparison['revenue_change'] / category_comparison['revenue_m1'].replace(0, np.nan) * 100)
            .fillna(0)
            .round(2)
        )
        
        category_comparison = category_comparison.sort_values('revenue_m2', ascending=False)
        
        return {
            'month1_metrics': month1_metrics,
            'month2_metrics': month2_metrics,
            'changes': changes,
            'month1_categories': month1_categories,
            'month2_categories': month2_categories,
            'category_comparison': category_comparison
        }
    
    def get_available_months(self) -> List[str]:
        """
        Get list of available months in the data.
        
        Returns:
            List of month strings in YYYY-MM format, sorted chronologically
        """
        df = self.data.copy()
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        months = sorted(df['year_month'].unique())
        return months

