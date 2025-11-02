"""Customer behavior analysis module."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from functools import lru_cache
import config


class CustomerAnalyzer:
    """Analyzes customer behavior and purchasing patterns."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize customer analyzer.
        
        Args:
            data: Preprocessed sales DataFrame
        """
        self.data = data
        self.current_date = data['date'].max()
        # Cache for expensive computations
        self._customer_summary_cache: Optional[pd.DataFrame] = None
        
    def get_customer_summary(self) -> pd.DataFrame:
        """Get summary statistics for each customer with refund handling. (CACHED)"""
        # Return cached result if available
        if self._customer_summary_cache is not None:
            return self._customer_summary_cache
        
        # Separate refunds from sales
        sales_data = self.data[~self.data['is_refund']]
        refunds_data = self.data[self.data['is_refund']]
        
        # Calculate sales metrics
        customer_stats = sales_data.groupby('customer_name').agg({
            'order_id': 'nunique',
            'total': 'sum',
            'quantity': 'sum',
            'date': ['min', 'max'],
            'item_name': 'nunique'
        }).reset_index()
        
        # Flatten column names
        customer_stats.columns = [
            'customer_name', 'total_orders', 'gross_spent', 'total_items',
            'first_purchase', 'last_purchase', 'unique_products'
        ]
        
        # Calculate refund metrics per customer
        customer_refunds = refunds_data.groupby('customer_name').agg({
            'total': lambda x: abs(x.sum()),
            'order_id': 'nunique',
            'quantity': lambda x: abs(x.sum())
        }).reset_index()
        customer_refunds.columns = ['customer_name', 'refund_amount', 'refund_orders', 'refund_quantity']
        
        # Merge refund data
        customer_stats = customer_stats.merge(customer_refunds, on='customer_name', how='left')
        customer_stats['refund_amount'] = customer_stats['refund_amount'].fillna(0)
        customer_stats['refund_orders'] = customer_stats['refund_orders'].fillna(0).astype(int)
        customer_stats['refund_quantity'] = customer_stats['refund_quantity'].fillna(0)
        
        # Calculate net spending
        customer_stats['total_spent'] = customer_stats['gross_spent'] - customer_stats['refund_amount']
        customer_stats['net_items'] = customer_stats['total_items'] - customer_stats['refund_quantity']
        
        # Calculate refund rate
        customer_stats['refund_rate_pct'] = (
            customer_stats['refund_amount'] / customer_stats['gross_spent'] * 100
        ).fillna(0)
        
        # Calculate additional metrics
        customer_stats['avg_order_value'] = customer_stats['total_spent'] / customer_stats['total_orders']
        customer_stats['days_as_customer'] = (
            customer_stats['last_purchase'] - customer_stats['first_purchase']
        ).dt.days + 1
        
        # Days since last purchase (use all data including refunds for recency)
        all_dates = self.data.groupby('customer_name')['date'].max()
        customer_stats = customer_stats.set_index('customer_name').join(all_dates.rename('most_recent_activity')).reset_index()
        customer_stats['days_since_last_purchase'] = (
            self.current_date - customer_stats['most_recent_activity']
        ).dt.days
        
        # Purchase frequency (orders per month)
        customer_stats['purchase_frequency'] = (
            customer_stats['total_orders'] / 
            (customer_stats['days_as_customer'] / 30)
        ).replace([np.inf, -np.inf], 0)
        
        result = customer_stats.sort_values('total_spent', ascending=False)
        
        # Cache the result
        self._customer_summary_cache = result
        
        return result
    
    def get_frequent_buyers(self, n: int = 20) -> pd.DataFrame:
        """Identify most frequent buyers."""
        customer_stats = self.get_customer_summary()
        return customer_stats.nlargest(n, 'total_orders')[
            ['customer_name', 'total_orders', 'total_spent', 'avg_order_value', 
             'last_purchase', 'days_since_last_purchase']
        ]
    
    def get_high_value_customers(self, n: int = 20) -> pd.DataFrame:
        """Identify high-value customers by total spend."""
        customer_stats = self.get_customer_summary()
        return customer_stats.nlargest(n, 'total_spent')[
            ['customer_name', 'total_spent', 'total_orders', 'avg_order_value',
             'last_purchase', 'unique_products']
        ]
    
    def get_churn_risk_customers(self, threshold_days: int = None) -> pd.DataFrame:
        """
        Identify customers at risk of churning.
        
        Args:
            threshold_days: Days of inactivity to consider churn risk
        """
        if threshold_days is None:
            threshold_days = config.CHURN_THRESHOLD_DAYS
        
        customer_stats = self.get_customer_summary()
        
        # Filter customers who haven't purchased recently
        churn_risk = customer_stats[
            customer_stats['days_since_last_purchase'] > threshold_days
        ].copy()
        
        # Calculate expected return date based on historical frequency
        churn_risk['expected_return_days'] = (
            30 / churn_risk['purchase_frequency'].replace(0, np.inf)
        ).replace([np.inf, -np.inf], 30)
        
        churn_risk['days_overdue'] = (
            churn_risk['days_since_last_purchase'] - churn_risk['expected_return_days']
        )
        
        # Sort by value (prioritize high-value customers)
        churn_risk = churn_risk.sort_values('total_spent', ascending=False)
        
        return churn_risk[
            ['customer_name', 'total_spent', 'total_orders', 'last_purchase',
             'days_since_last_purchase', 'days_overdue', 'purchase_frequency']
        ]
    
    def get_new_customers(self, days: int = 30) -> pd.DataFrame:
        """Identify customers who made their first purchase recently."""
        customer_stats = self.get_customer_summary()
        
        cutoff_date = self.current_date - timedelta(days=days)
        new_customers = customer_stats[
            customer_stats['first_purchase'] >= cutoff_date
        ].copy()
        
        return new_customers.sort_values('first_purchase', ascending=False)[
            ['customer_name', 'first_purchase', 'total_orders', 'total_spent', 'unique_products']
        ]
    
    def get_repeat_purchase_rate(self) -> Dict:
        """Calculate repeat purchase metrics."""
        customer_stats = self.get_customer_summary()
        
        total_customers = len(customer_stats)
        repeat_customers = len(customer_stats[customer_stats['total_orders'] > 1])
        one_time_customers = len(customer_stats[customer_stats['total_orders'] == 1])
        
        repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        # Average orders per customer
        avg_orders_per_customer = customer_stats['total_orders'].mean()
        
        # Customer lifetime value
        avg_customer_ltv = customer_stats['total_spent'].mean()
        
        return {
            'total_customers': total_customers,
            'repeat_customers': repeat_customers,
            'one_time_customers': one_time_customers,
            'repeat_rate_pct': repeat_rate,
            'avg_orders_per_customer': avg_orders_per_customer,
            'avg_customer_ltv': avg_customer_ltv
        }
    
    def get_customer_cohorts(self) -> pd.DataFrame:
        """Analyze customer cohorts based on first purchase month."""
        df = self.data.copy()
        
        # Get first purchase date for each customer
        first_purchase = df.groupby('customer_name')['date'].min().reset_index()
        first_purchase.columns = ['customer_name', 'cohort_date']
        first_purchase['cohort_month'] = first_purchase['cohort_date'].dt.to_period('M')
        
        # Merge with main data
        df = df.merge(first_purchase[['customer_name', 'cohort_month']], on='customer_name')
        df['order_month'] = df['date'].dt.to_period('M')
        
        # Calculate months since first purchase
        df['months_since_first'] = (
            (df['order_month'] - df['cohort_month']).apply(lambda x: x.n)
        )
        
        # Create cohort analysis
        cohort_data = df.groupby(['cohort_month', 'months_since_first']).agg({
            'customer_name': 'nunique',
            'total': 'sum'
        }).reset_index()
        
        cohort_data.columns = ['cohort_month', 'months_since_first', 'customers', 'revenue']
        
        # Pivot for cohort table
        cohort_counts = cohort_data.pivot(
            index='cohort_month', 
            columns='months_since_first', 
            values='customers'
        )
        
        # Calculate retention rates
        cohort_sizes = cohort_counts.iloc[:, 0]
        retention_rates = cohort_counts.divide(cohort_sizes, axis=0) * 100
        
        return retention_rates
    
    def get_customer_segments_by_value(self) -> Dict:
        """Segment customers by spending levels."""
        customer_stats = self.get_customer_summary()
        
        # Define percentile-based segments
        high_value_threshold = customer_stats['total_spent'].quantile(0.80)
        medium_value_threshold = customer_stats['total_spent'].quantile(0.50)
        
        high_value = customer_stats[customer_stats['total_spent'] >= high_value_threshold]
        medium_value = customer_stats[
            (customer_stats['total_spent'] >= medium_value_threshold) & 
            (customer_stats['total_spent'] < high_value_threshold)
        ]
        low_value = customer_stats[customer_stats['total_spent'] < medium_value_threshold]
        
        return {
            'high_value': {
                'count': len(high_value),
                'total_revenue': high_value['total_spent'].sum(),
                'avg_spent': high_value['total_spent'].mean(),
                'revenue_contribution_pct': (
                    high_value['total_spent'].sum() / customer_stats['total_spent'].sum() * 100
                )
            },
            'medium_value': {
                'count': len(medium_value),
                'total_revenue': medium_value['total_spent'].sum(),
                'avg_spent': medium_value['total_spent'].mean(),
                'revenue_contribution_pct': (
                    medium_value['total_spent'].sum() / customer_stats['total_spent'].sum() * 100
                )
            },
            'low_value': {
                'count': len(low_value),
                'total_revenue': low_value['total_spent'].sum(),
                'avg_spent': low_value['total_spent'].mean(),
                'revenue_contribution_pct': (
                    low_value['total_spent'].sum() / customer_stats['total_spent'].sum() * 100
                )
            }
        }
    
    def get_customer_purchase_intervals(self) -> pd.DataFrame:
        """Calculate average time between purchases for each customer."""
        # Get orders for each customer
        customer_orders = self.data.groupby(['customer_name', 'order_id'])['date'].min().reset_index()
        customer_orders = customer_orders.sort_values(['customer_name', 'date'])
        
        # Calculate intervals
        intervals = []
        for customer in customer_orders['customer_name'].unique():
            customer_dates = customer_orders[
                customer_orders['customer_name'] == customer
            ]['date'].values
            
            if len(customer_dates) > 1:
                # Calculate days between consecutive purchases
                date_diffs = np.diff(customer_dates).astype('timedelta64[D]').astype(int)
                
                intervals.append({
                    'customer_name': customer,
                    'num_orders': len(customer_dates),
                    'avg_interval_days': np.mean(date_diffs),
                    'median_interval_days': np.median(date_diffs),
                    'std_interval_days': np.std(date_diffs),
                    'min_interval_days': np.min(date_diffs),
                    'max_interval_days': np.max(date_diffs)
                })
        
        return pd.DataFrame(intervals).sort_values('avg_interval_days')
    
    def get_customer_product_preferences(self, customer_name: str) -> pd.DataFrame:
        """Get product purchase history and preferences for a specific customer."""
        customer_data = self.data[self.data['customer_name'] == customer_name].copy()
        
        if len(customer_data) == 0:
            return pd.DataFrame()
        
        product_prefs = customer_data.groupby(['item_code', 'item_name', 'category']).agg({
            'order_id': 'nunique',
            'quantity': 'sum',
            'total': 'sum',
            'date': ['min', 'max']
        }).reset_index()
        
        product_prefs.columns = [
            'item_code', 'item_name', 'category', 'times_purchased',
            'total_quantity', 'total_spent', 'first_purchase', 'last_purchase'
        ]
        
        product_prefs['days_since_last_purchase'] = (
            self.current_date - product_prefs['last_purchase']
        ).dt.days
        
        return product_prefs.sort_values('times_purchased', ascending=False)

