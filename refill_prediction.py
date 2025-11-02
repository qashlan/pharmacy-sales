"""Advanced refill prediction module for pharmaceutical products."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.stats import linregress
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')


class RefillPredictor:
    """Predicts when customers will need product refills based on purchase history."""
    
    # Version number for cache invalidation when calculation logic changes
    CALCULATION_VERSION = "2.0"  # Updated for 7-factor confidence scoring
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize refill predictor.
        
        Args:
            data: Preprocessed sales DataFrame
        """
        self.data = data
        self.current_date = data['date'].max()
        self.customer_product_intervals: Optional[pd.DataFrame] = None
        
    def calculate_purchase_intervals(self, include_price_prediction: bool = True) -> pd.DataFrame:
        """
        Calculate purchase intervals for each customer-product pair with refund handling. (CACHED)
        
        Returns:
            DataFrame with average purchase intervals and statistics
        """
        # Return cached result if available
        if self.customer_product_intervals is not None:
            return self.customer_product_intervals
        
        # Exclude "Unknown Customer" and refunds from refill predictions
        # Unknown customers are walk-ins without identifiable info, so tracking refill patterns is not meaningful
        # Refunds don't represent actual consumption/usage patterns
        data_for_refills = self.data[
            (self.data['customer_name'] != 'Unknown Customer') &
            (~self.data['is_refund'])
        ].copy()
        
        num_refunds_excluded = len(self.data[self.data['is_refund']])
        if num_refunds_excluded > 0:
            print(f"ℹ Refill prediction: Excluded {num_refunds_excluded} refund transactions from analysis")
        
        # Group by customer and product
        customer_product_purchases = data_for_refills.groupby(
            ['customer_name', 'item_code', 'item_name']
        )['date'].apply(list).reset_index()
        
        intervals_data = []
        
        for _, row in customer_product_purchases.iterrows():
            customer = row['customer_name']
            item_code = row['item_code']
            item_name = row['item_name']
            purchase_dates = sorted(row['date'])
            
            # Need at least 2 purchases to calculate interval
            if len(purchase_dates) < 2:
                continue
            
            # Track first order date for relationship age calculation
            first_order_date = min(purchase_dates)
            
            # Get purchase details for this customer-product pair
            purchase_data = data_for_refills[
                (data_for_refills['customer_name'] == customer) &
                (data_for_refills['item_name'] == item_name)
            ].sort_values('date')
            
            # Calculate intervals between consecutive purchases
            intervals = []
            prices = []
            quantities = []
            
            for i in range(1, len(purchase_dates)):
                interval_days = (purchase_dates[i] - purchase_dates[i-1]).days
                intervals.append(interval_days)
            
            # Get pricing history
            for date in purchase_dates:
                purchase_on_date = purchase_data[purchase_data['date'] == date]
                avg_price = purchase_on_date['total'].sum() / purchase_on_date['quantity'].sum() if purchase_on_date['quantity'].sum() > 0 else 0
                prices.append(avg_price)
                quantities.append(purchase_on_date['quantity'].sum())
            
            # Calculate interval statistics
            avg_interval = np.mean(intervals)
            median_interval = np.median(intervals)
            std_interval = np.std(intervals) if len(intervals) > 1 else 0
            min_interval = np.min(intervals)
            max_interval = np.max(intervals)
            
            # Calculate price statistics
            avg_price = np.mean(prices)
            price_trend = 0
            predicted_price = avg_price
            
            if len(prices) >= 3:
                # Linear regression for price trend
                x = np.arange(len(prices))
                slope, intercept, r_value, p_value, std_err = linregress(x, prices)
                price_trend = slope
                # Predict next purchase price
                predicted_price = slope * len(prices) + intercept
                predicted_price = max(predicted_price, 0)  # Ensure non-negative
            
            # Advanced interval prediction with trend analysis
            if len(intervals) >= 3:
                # Check for trend in intervals (getting more or less frequent)
                x = np.arange(len(intervals))
                interval_slope, _, _, _, _ = linregress(x, intervals)
                # Weighted average giving more weight to recent intervals
                weights = np.exp(np.linspace(-1, 0, len(intervals)))
                weights = weights / weights.sum()
                weighted_avg_interval = np.average(intervals, weights=weights)
                predicted_interval = weighted_avg_interval + (interval_slope * len(intervals))
                predicted_interval = max(predicted_interval, min_interval)  # Don't predict too short
            else:
                predicted_interval = avg_interval
            
            # Get last purchase date
            last_purchase = purchase_dates[-1]
            days_since_last = (self.current_date - last_purchase).days
            
            # Predict next purchase date using advanced interval
            predicted_next_purchase = last_purchase + timedelta(days=int(predicted_interval))
            days_until_predicted = (predicted_next_purchase - self.current_date).days
            
            # ===== ADVANCED MULTI-FACTOR CONFIDENCE CALCULATION =====
            
            # Factor 1: Trend Stability (25% weight)
            # Measures how consistent the interval changes are
            trend_stability_score = 100  # Default for insufficient data
            if len(intervals) >= 3:
                interval_deltas = [intervals[i] - intervals[i-1] for i in range(1, len(intervals))]
                if len(interval_deltas) > 0:
                    delta_std = np.std(interval_deltas)
                    delta_mean = np.mean(np.abs(interval_deltas))
                    if delta_mean > 0:
                        delta_cv = delta_std / delta_mean
                        trend_stability_score = max(0, min(100, 100 * (1 - min(delta_cv, 1))))
                    else:
                        trend_stability_score = 100  # Perfect stability
            
            # Factor 2: Customer Relationship Age (20% weight)
            # Longer relationships provide more reliable patterns
            relationship_days = (self.current_date - first_order_date).days
            # Logarithmic scaling: rapid increase initially, then diminishes
            # 30 days = ~50%, 90 days = ~70%, 365 days = ~90%, 730+ days = ~95%
            if relationship_days > 0:
                relationship_age_score = min(100, 100 * (np.log1p(relationship_days) / np.log1p(730)))
            else:
                relationship_age_score = 0
            
            # Factor 3: Seasonal Consistency (10% weight)
            # Check if purchases follow consistent seasonal patterns
            seasonal_consistency_score = 50  # Default neutral
            if len(purchase_dates) >= 4:
                months = [d.month for d in purchase_dates]
                # Check variance in months - low variance means seasonal pattern
                month_std = np.std(months)
                # If all purchases in similar months (low std), higher score
                seasonal_consistency_score = max(0, min(100, 100 * (1 - month_std / 6)))
            
            # Factor 4: Quantity Consistency (15% weight)
            # Consistent order quantities indicate predictable behavior
            quantity_consistency_score = 50  # Default
            if len(quantities) >= 2 and np.mean(quantities) > 0:
                quantity_cv = np.std(quantities) / np.mean(quantities)
                quantity_consistency_score = max(0, min(100, 100 * (1 - min(quantity_cv, 1))))
            
            # Factor 5: Price Stability (10% weight)
            # Price volatility may affect purchase timing
            price_stability_score = 50  # Default
            if len(prices) >= 2 and np.mean(prices) > 0:
                price_cv = np.std(prices) / np.mean(prices)
                price_stability_score = max(0, min(100, 100 * (1 - min(price_cv, 1))))
            
            # Factor 6: Gap Analysis (10% weight)
            # Recent anomalies reduce confidence
            gap_analysis_score = 100  # Default: no recent anomalies
            if len(intervals) >= 2:
                recent_gap = intervals[-1]
                avg_previous_gaps = np.mean(intervals[:-1])
                if avg_previous_gaps > 0:
                    gap_ratio = recent_gap / avg_previous_gaps
                    # If recent gap is 2x longer or shorter, reduce confidence
                    if gap_ratio > 2 or gap_ratio < 0.5:
                        gap_analysis_score = max(0, 100 * (1 - abs(gap_ratio - 1) / 2))
            
            # Factor 7: Data Volume & Recency (10% weight)
            # More data and recent purchases increase confidence
            data_volume_score = min(100, (len(purchase_dates) / 10) * 100)
            recency_factor = max(0, 1 - (days_since_last / avg_interval)) if avg_interval > 0 else 0.5
            data_recency_score = (data_volume_score * 0.5 + recency_factor * 100 * 0.5)
            
            # Combined weighted confidence score
            confidence = (
                trend_stability_score * 0.25 +
                relationship_age_score * 0.20 +
                quantity_consistency_score * 0.15 +
                seasonal_consistency_score * 0.10 +
                price_stability_score * 0.10 +
                gap_analysis_score * 0.10 +
                data_recency_score * 0.10
            )
            
            confidence = max(0, min(100, confidence))
            
            # Calculate quantity trend
            avg_quantity = np.mean(quantities)
            quantity_trend = 0
            if len(quantities) >= 3:
                x = np.arange(len(quantities))
                quantity_slope, _, _, _, _ = linregress(x, quantities)
                quantity_trend = quantity_slope
            
            # Predict order value
            predicted_quantity = avg_quantity + (quantity_trend * len(quantities)) if len(quantities) >= 3 else avg_quantity
            predicted_quantity = max(predicted_quantity, 1)  # Ensure at least 1
            predicted_order_value = predicted_price * predicted_quantity
            
            # Calculate purchase regularity score (0-100)
            if std_interval > 0 and avg_interval > 0:
                coefficient_of_variation = std_interval / avg_interval
                regularity_score = 100 - (coefficient_of_variation * 100)
            else:
                regularity_score = 50
            regularity_score = max(0, min(100, regularity_score))
            
            intervals_data.append({
                'customer_name': customer,
                'item_code': item_code,
                'item_name': item_name,
                'num_purchases': len(purchase_dates),
                'first_order_date': first_order_date,
                'last_purchase_date': last_purchase,
                'days_since_first_order': (self.current_date - first_order_date).days,
                'days_since_last_purchase': days_since_last,
                'avg_interval_days': avg_interval,
                'median_interval_days': median_interval,
                'std_interval_days': std_interval,
                'min_interval_days': min_interval,
                'max_interval_days': max_interval,
                'predicted_next_purchase': predicted_next_purchase,
                'days_until_predicted': days_until_predicted,
                'confidence_score': confidence,
                'regularity_score': regularity_score,
                'avg_price_per_unit': avg_price,
                'price_trend': price_trend,
                'predicted_unit_price': predicted_price,
                'avg_quantity': avg_quantity,
                'quantity_trend': quantity_trend,
                'predicted_quantity': predicted_quantity,
                'predicted_order_value': predicted_order_value,
                'total_lifetime_value': purchase_data['total'].sum()
            })
        
        self.customer_product_intervals = pd.DataFrame(intervals_data)
        return self.customer_product_intervals
    
    def get_overdue_refills(self, tolerance_days: int = 7) -> pd.DataFrame:
        """
        Identify customers who are overdue for refills.
        
        Args:
            tolerance_days: Grace period after predicted date
        """
        if self.customer_product_intervals is None:
            self.calculate_purchase_intervals()
        
        # Force recalculation if new columns are missing (cache invalidation)
        if 'first_order_date' not in self.customer_product_intervals.columns:
            self.customer_product_intervals = None
            self.calculate_purchase_intervals()
        
        # Filter overdue refills
        overdue = self.customer_product_intervals[
            self.customer_product_intervals['days_until_predicted'] < -tolerance_days
        ].copy()
        
        # Calculate how many days overdue
        overdue['days_overdue'] = -overdue['days_until_predicted']
        
        # Classify customer status based on how overdue they are
        # Business rule: 6+ months overdue = likely lost customer
        def classify_overdue_status(row):
            days_overdue = row['days_overdue']
            if days_overdue >= 180:  # 6+ months
                return 'Likely Lost'
            elif days_overdue >= 90:  # 3-6 months
                return 'At High Risk'
            elif days_overdue >= 30:  # 1-3 months
                return 'At Risk'
            else:
                return 'Action Needed'
        
        overdue['customer_status'] = overdue.apply(classify_overdue_status, axis=1)
        
        # Adjust confidence for overdue customers (reduce confidence as overdue increases)
        def adjust_confidence_for_overdue(row):
            original_confidence = row['confidence_score']
            days_overdue = row['days_overdue']
            
            # Reduce confidence based on how overdue
            if days_overdue >= 180:  # 6+ months - very low chance of return
                return min(original_confidence * 0.2, 20)  # Max 20% confidence
            elif days_overdue >= 90:  # 3-6 months - low chance
                return original_confidence * 0.4
            elif days_overdue >= 60:  # 2-3 months - moderate reduction
                return original_confidence * 0.6
            elif days_overdue >= 30:  # 1-2 months - small reduction
                return original_confidence * 0.8
            else:
                return original_confidence * 0.9  # Slight reduction
        
        overdue['adjusted_confidence'] = overdue.apply(adjust_confidence_for_overdue, axis=1)
        overdue['adjusted_confidence'] = overdue['adjusted_confidence'].round(1)
        
        # Calculate churn probability (inverse of adjusted confidence)
        overdue['churn_probability'] = (100 - overdue['adjusted_confidence']).round(1)
        
        # Sort by days overdue (most urgent first)
        overdue = overdue.sort_values('days_overdue', ascending=False)
        
        return overdue[
            ['customer_name', 'item_name', 'first_order_date', 'last_purchase_date', 
             'predicted_next_purchase', 'days_overdue', 'avg_interval_days',
             'num_purchases', 'days_since_first_order', 'customer_status',
             'confidence_score', 'adjusted_confidence', 'churn_probability',
             'predicted_order_value', 'predicted_unit_price', 'predicted_quantity',
             'total_lifetime_value']
        ]
    
    def get_upcoming_refills(self, days_ahead: int = 30) -> pd.DataFrame:
        """
        Identify customers expected to need refills soon.
        
        Args:
            days_ahead: Number of days to look ahead
        """
        if self.customer_product_intervals is None:
            self.calculate_purchase_intervals()
        
        # Force recalculation if new columns are missing (cache invalidation)
        if 'first_order_date' not in self.customer_product_intervals.columns:
            self.customer_product_intervals = None
            self.calculate_purchase_intervals()
        
        # Filter upcoming refills
        upcoming = self.customer_product_intervals[
            (self.customer_product_intervals['days_until_predicted'] >= 0) &
            (self.customer_product_intervals['days_until_predicted'] <= days_ahead)
        ].copy()
        
        # Sort by predicted date (soonest first)
        upcoming = upcoming.sort_values('days_until_predicted')
        
        return upcoming[
            ['customer_name', 'item_name', 'first_order_date', 'last_purchase_date',
             'predicted_next_purchase', 'predicted_order_value', 'days_until_predicted', 
             'avg_interval_days', 'num_purchases', 'days_since_first_order', 
             'confidence_score', 'predicted_unit_price', 'predicted_quantity',
             'avg_price_per_unit', 'total_lifetime_value']
        ]
    
    def get_customer_refill_schedule(self, customer_name: str) -> pd.DataFrame:
        """Get complete refill schedule for a specific customer."""
        if self.customer_product_intervals is None:
            self.calculate_purchase_intervals()
        
        # Force recalculation if new columns are missing (cache invalidation)
        if 'first_order_date' not in self.customer_product_intervals.columns:
            self.customer_product_intervals = None
            self.calculate_purchase_intervals()
        
        customer_schedule = self.customer_product_intervals[
            self.customer_product_intervals['customer_name'] == customer_name
        ].copy()
        
        # Add refill status
        def determine_status(row):
            days_until = row['days_until_predicted']
            if days_until < -7:
                return 'Overdue'
            elif days_until < 0:
                return 'Due Now'
            elif days_until <= 7:
                return 'Due Soon'
            elif days_until <= 30:
                return 'Upcoming'
            else:
                return 'Future'
        
        customer_schedule['refill_status'] = customer_schedule.apply(determine_status, axis=1)
        
        # Sort by urgency
        status_order = {'Overdue': 0, 'Due Now': 1, 'Due Soon': 2, 'Upcoming': 3, 'Future': 4}
        customer_schedule['status_order'] = customer_schedule['refill_status'].map(status_order)
        customer_schedule = customer_schedule.sort_values('status_order')
        
        return customer_schedule[
            ['item_name', 'refill_status', 'first_order_date', 'last_purchase_date',
             'predicted_next_purchase', 'days_until_predicted', 'avg_interval_days',
             'num_purchases', 'days_since_first_order', 'confidence_score',
             'predicted_order_value', 'predicted_unit_price', 'predicted_quantity',
             'total_lifetime_value']
        ]
    
    def get_product_refill_patterns(self, item_name: str) -> pd.DataFrame:
        """Analyze refill patterns for a specific product across all customers."""
        if self.customer_product_intervals is None:
            self.calculate_purchase_intervals()
        
        # Force recalculation if new columns are missing (cache invalidation)
        if 'first_order_date' not in self.customer_product_intervals.columns:
            self.customer_product_intervals = None
            self.calculate_purchase_intervals()
        
        product_patterns = self.customer_product_intervals[
            self.customer_product_intervals['item_name'] == item_name
        ].copy()
        
        if len(product_patterns) == 0:
            return pd.DataFrame()
        
        # Sort by average interval to identify different usage patterns
        product_patterns = product_patterns.sort_values('avg_interval_days')
        
        # Categorize customers by refill frequency
        intervals = product_patterns['avg_interval_days'].values
        q1, q2, q3 = np.percentile(intervals, [25, 50, 75])
        
        def categorize_frequency(interval):
            if interval <= q1:
                return 'Very Frequent'
            elif interval <= q2:
                return 'Frequent'
            elif interval <= q3:
                return 'Moderate'
            else:
                return 'Infrequent'
        
        product_patterns['refill_frequency_category'] = product_patterns['avg_interval_days'].apply(
            categorize_frequency
        )
        
        return product_patterns[
            ['customer_name', 'avg_interval_days', 'refill_frequency_category',
             'num_purchases', 'first_order_date', 'last_purchase_date', 
             'predicted_next_purchase', 'days_since_first_order', 'confidence_score']
        ]
    
    def get_refill_compliance_score(self) -> pd.DataFrame:
        """
        Calculate refill compliance scores for customers.
        
        Higher scores indicate more consistent refill behavior.
        """
        if self.customer_product_intervals is None:
            self.calculate_purchase_intervals()
        
        # Force recalculation if new columns are missing (cache invalidation)
        if 'first_order_date' not in self.customer_product_intervals.columns:
            self.customer_product_intervals = None
            self.calculate_purchase_intervals()
        
        # Group by customer
        customer_compliance = self.customer_product_intervals.groupby('customer_name').agg({
            'confidence_score': 'mean',
            'num_purchases': 'sum',
            'avg_interval_days': 'mean',
            'std_interval_days': 'mean',
            'item_name': 'count'  # Number of different products
        }).reset_index()
        
        customer_compliance.columns = [
            'customer_name', 'avg_confidence', 'total_repeat_purchases',
            'avg_interval_days', 'avg_std_days', 'num_products_refilled'
        ]
        
        # Calculate overall compliance score (0-100)
        # Based on: consistency (confidence), number of refills, and number of products
        customer_compliance['compliance_score'] = (
            customer_compliance['avg_confidence'] * 0.5 +
            np.minimum(customer_compliance['total_repeat_purchases'] * 5, 30) +
            np.minimum(customer_compliance['num_products_refilled'] * 5, 20)
        )
        
        customer_compliance = customer_compliance.sort_values('compliance_score', ascending=False)
        
        return customer_compliance
    
    def get_refill_summary_stats(self) -> Dict:
        """Get summary statistics for refill predictions."""
        if self.customer_product_intervals is None:
            self.calculate_purchase_intervals()
        
        # Force recalculation if new columns are missing (cache invalidation)
        if 'first_order_date' not in self.customer_product_intervals.columns:
            self.customer_product_intervals = None
            self.calculate_purchase_intervals()
        
        intervals = self.customer_product_intervals
        
        # Overall statistics
        total_refill_pairs = len(intervals)
        avg_refill_interval = intervals['avg_interval_days'].mean()
        median_refill_interval = intervals['avg_interval_days'].median()
        
        # Overdue refills
        overdue = intervals[intervals['days_until_predicted'] < -7]
        num_overdue = len(overdue)
        
        # Upcoming refills (next 30 days)
        upcoming = intervals[
            (intervals['days_until_predicted'] >= 0) &
            (intervals['days_until_predicted'] <= 30)
        ]
        num_upcoming = len(upcoming)
        
        # High confidence predictions
        high_confidence = intervals[intervals['confidence_score'] >= 70]
        num_high_confidence = len(high_confidence)
        
        # Average purchases per customer-product pair
        avg_purchases = intervals['num_purchases'].mean()
        
        return {
            'total_refill_pairs': total_refill_pairs,
            'avg_refill_interval_days': avg_refill_interval,
            'median_refill_interval_days': median_refill_interval,
            'num_overdue_refills': num_overdue,
            'num_upcoming_refills_30d': num_upcoming,
            'num_high_confidence_predictions': num_high_confidence,
            'high_confidence_pct': (num_high_confidence / total_refill_pairs * 100) if total_refill_pairs > 0 else 0,
            'avg_purchases_per_pair': avg_purchases
        }
    
    def identify_irregular_refill_patterns(self) -> pd.DataFrame:
        """
        Identify customer-product pairs with irregular refill patterns.
        
        These may indicate:
        - Changed medication needs
        - Non-compliance
        - Switching to competitors
        """
        if self.customer_product_intervals is None:
            self.calculate_purchase_intervals()
        
        # Force recalculation if new columns are missing (cache invalidation)
        if 'first_order_date' not in self.customer_product_intervals.columns:
            self.customer_product_intervals = None
            self.calculate_purchase_intervals()
        
        intervals = self.customer_product_intervals.copy()
        
        # Calculate coefficient of variation
        intervals['cv'] = intervals['std_interval_days'] / intervals['avg_interval_days']
        
        # Identify irregular patterns (high CV and/or low confidence)
        irregular = intervals[
            (intervals['cv'] > 0.5) | (intervals['confidence_score'] < 50)
        ].copy()
        
        irregular = irregular.sort_values('cv', ascending=False)
        
        return irregular[
            ['customer_name', 'item_name', 'num_purchases', 'avg_interval_days',
             'std_interval_days', 'cv', 'confidence_score', 'last_purchase_date',
             'days_since_last_purchase']
        ]
    
    def get_likely_lost_customers(self, min_overdue_days: int = 180) -> pd.DataFrame:
        """
        Identify customers who are likely lost (very overdue and unlikely to return).
        
        Business Rule: Customers overdue by 6+ months are likely lost.
        
        Args:
            min_overdue_days: Minimum days overdue to consider lost (default: 180 = 6 months)
        
        Returns:
            DataFrame with likely lost customers and their details
        """
        if self.customer_product_intervals is None:
            self.calculate_purchase_intervals()
        
        # Force recalculation if new columns are missing (cache invalidation)
        if 'first_order_date' not in self.customer_product_intervals.columns:
            self.customer_product_intervals = None
            self.calculate_purchase_intervals()
        
        # Filter for overdue customers
        overdue = self.customer_product_intervals[
            self.customer_product_intervals['days_until_predicted'] < 0
        ].copy()
        
        overdue['days_overdue'] = -overdue['days_until_predicted']
        
        # Filter for likely lost customers (6+ months overdue by default)
        lost = overdue[overdue['days_overdue'] >= min_overdue_days].copy()
        
        # Calculate lifetime value for prioritization
        lost['potential_recovery_value'] = lost['total_lifetime_value']
        
        # Sort by lifetime value (prioritize high-value lost customers)
        lost = lost.sort_values('total_lifetime_value', ascending=False)
        
        return lost[
            ['customer_name', 'item_name', 'first_order_date', 'last_purchase_date',
             'days_since_last_purchase', 'days_overdue', 'avg_interval_days',
             'num_purchases', 'total_lifetime_value', 'potential_recovery_value']
        ]
    
    def get_seasonal_refill_patterns(self) -> pd.DataFrame:
        """Analyze if refill patterns vary by season or month."""
        # Exclude "Unknown Customer" and refunds from seasonal refill analysis
        data_for_analysis = self.data[
            (self.data['customer_name'] != 'Unknown Customer') &
            (~self.data['is_refund'])
        ].copy()
        
        # Group purchases by month
        monthly_refills = data_for_analysis.groupby(['month', 'item_name']).agg({
            'customer_name': 'nunique',
            'quantity': 'sum',
            'total': 'sum'
        }).reset_index()
        
        monthly_refills.columns = ['month', 'item_name', 'unique_customers', 'quantity', 'revenue']
        
        # Calculate month-over-month variation for each product
        seasonal_data = []
        
        for item in monthly_refills['item_name'].unique():
            item_data = monthly_refills[monthly_refills['item_name'] == item]
            
            if len(item_data) >= 3:  # Need at least 3 months of data
                monthly_quantities = item_data['quantity'].values
                
                # Calculate coefficient of variation
                mean_qty = np.mean(monthly_quantities)
                std_qty = np.std(monthly_quantities)
                cv = (std_qty / mean_qty) if mean_qty > 0 else 0
                
                # Identify peak month
                peak_month = item_data.loc[item_data['quantity'].idxmax(), 'month']
                
                seasonal_data.append({
                    'item_name': item,
                    'avg_monthly_quantity': mean_qty,
                    'std_monthly_quantity': std_qty,
                    'coefficient_variation': cv,
                    'peak_month': peak_month,
                    'seasonality_score': cv * 100  # Higher = more seasonal
                })
        
        seasonal_df = pd.DataFrame(seasonal_data)
        seasonal_df = seasonal_df.sort_values('seasonality_score', ascending=False)
        
        return seasonal_df

